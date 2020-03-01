# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 13:51:41 2020

@author: Shadow
"""

from tensorflow.keras.models import model_from_json
from tensorflow.keras.optimizers import Adam
import numpy as np

from utils.config import CONFIG
from generalIOLib import FlatInputDic, GeneralOutputLib, getTiles, shiftTile
from generalBDDHandler import GeneralBDDHandler, convertStability

"""
Player that will play according to a model
"""
class ModelPlayer:
    def __init__(self, model_name, directory):
        
        json_file = open( f"{directory}/{model_name}.json", 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights(f"{directory}/{model_name}.h5")
         
        # compile the model
        self.model.compile(loss='categorical_crossentropy', optimizer=Adam())
    
        self.flatInputLib = FlatInputDic()
        self.outputLib = GeneralOutputLib()
        self.generalBDDHandler = GeneralBDDHandler()
        self.player_tiles = list(filter(lambda x: x[1] < 14, getTiles()))
        self.player_spawns = list(filter( lambda x: (x[0] + x[1] == 13) or (x[0] - x[1] == 14), self.player_tiles))
        
    def updateIllegalActions(self, image, flat_inputs, predictions):
        n_cores = flat_inputs[1]
        n_bits = flat_inputs[2]
        
        
        # remove unaffordable firewalls:
        for unit_type in range(3):
            if(n_cores < CONFIG['cost'][unit_type]):
                for x,y in self.player_tiles:
                    action_num = self.outputLib.dic["{}_{}_{}".format(x,y,unit_type)]
                    predictions[action_num] = -np.inf
                    
        # remove unaffordable informations
        for unit_type in range(3,6):
            if(n_bits < CONFIG['cost'][unit_type]):
                for x,y in self.player_spawns:
                    action_num = self.outputLib.dic["{}_{}_{}".format(x,y,unit_type)]
                    predictions[action_num] = -np.inf
                
       # remove empty removals or already occupied spawns
        for x,y in self.player_tiles:
            u,v = shiftTile(x, y)
            already_removed = image[u][v][6]> 0
            
            occupied_by_firewalls = False
            for unit_type in range(3):
                occupied_by_firewalls = occupied_by_firewalls or image[u][v][unit_type] > 0
                
            occupied_by_information = False
            if((x + y == 13) or (x - y == 14)):
                for unit_type in range(3,6):
                    occupied_by_information = occupied_by_information or image[u][v][unit_type] > 0
                
            if not(occupied_by_firewalls) or already_removed:
                action_num = self.outputLib.dic["{}_{}_{}".format(x,y,6)]
                predictions[action_num] = -np.inf
            
            if occupied_by_firewalls or occupied_by_information:
                end_range = 6 if occupied_by_firewalls else 3
                for unit_type in range(end_range):
                    try:
                        action_num = self.outputLib.dic["{}_{}_{}".format(x,y,unit_type)]
                        predictions[action_num] = -np.inf 
                    except:
                        pass

    def constructInputs(self, units_list, players_stats, num_turn):
        flat_inputs = np.array(players_stats[0][:3] + players_stats[1][:3] + [num_turn])
        flat_input_dividers = np.array([30,50,30,30,50,30,100])
        flat_inputs = flat_inputs / flat_input_dividers
        image = self.generalBDDHandler.getImage(units_list)
        return image, flat_inputs
        
    def getNextAction(self, image, flat_inputs):
        predictions = self.model.predict((flat_inputs.reshape((1,7)), image.reshape((1,29,15,7))))[0]
        self.updateIllegalActions(image, flat_inputs, predictions)
        return np.argmax(predictions)
    
    def updateInputs(self, chosen_action, image, flat_inputs):
        x,y,unit_type = list(map(int, chosen_action.split('_')))
        if unit_type < 3:
            flat_inputs[1] -= CONFIG['cost'][unit_type]
        elif unit_type < 6:
            flat_inputs[2] -= CONFIG['cost'][unit_type]
            
        u,v = shiftTile(x,y)
        image[u][v][unit_type] += convertStability(unit_type,CONFIG['stabilities'][unit_type], False)

    def getTurnActions(self, units_list, players_stats, num_turn):
        image,flat_inputs = model_player.constructInputs(units_list, players_stats, num_turn)
        turn_actions = []
        while True:
            chosen_action = self.outputLib.column_names[self.getNextAction(image, flat_inputs)]
            turn_actions.append(chosen_action)
            if chosen_action == 'stop':
                break
            else:
                self.updateInputs(chosen_action, image, flat_inputs)
        return turn_actions


players_stats = [[30,45,5],[30,45,5]]
units_list = []
num_turn = 0
model_player = ModelPlayer('model_2_7649','models')
turn_actions = model_player.getTurnActions(units_list, players_stats, num_turn)
print(turn_actions)