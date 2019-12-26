#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 15:44:01 2019

@author: etiennew
"""


import re
import os
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import generalIOLib
from utils.config import getTiles

class GeneralBDDHandler:
    
    def __init__(self):
        
        self.bdd_name = "generalIO"
        self.bdd_path = 'datasets/' + self.bdd_name + '.pkl'
        
        self.images_path = 'cnn_images/'
        
        self.matrixInputs = generalIOLib.MatrixInput()
        self.flatInputsDic = generalIOLib.FlatInputDic()
        
        self.bdd = self.getBDD()
        
        self.depth = 3
        self.d_digits = [3 for d in range(self.depth)]
        self.d_counts = [0 for d in range(self.depth)]
        self.d_max = [10**(d) - 1 for d in self.d_digits]
        try:
            index = pd.read_csv(self.bdd_path,usecols = ['image_path'])
            last_image_path = index.iloc[index.shape[0]-1]['image_path']
            image_name = re.split('/',last_image_path)[-1]
            index_count = 0
            for d in range(self.depth):
                self.d_counts[d] = int(image_name[index_count:index_count + self.d_digits[d]])
                index_count += self.d_digits[d]
            self.updateCounts()
        except Exception:
            pass
    
    """
    update the image count according to the bdd
    """
    def __updateImageCount(self):
        image_names = list(self.bdd['image_name'])
        image_names.sort()
        self.d_counts = [0 for d in range(self.depth)]
        if(len(image_names)):
            last_image_name = image_names[-1]
            index_count = 0
            for d in range(self.depth):
                self.d_counts[d] = int(last_image_name[index_count:index_count + self.d_digits[d]])
                index_count += self.d_digits[d]
            self.__addCount()
            
    """
    update the counts to the next image
    """
    def __addCount(self):
        self.d_counts[self.depth - 1] += 1
        for i in range(self.depth - 1,-1,-1):
            if(self.d_counts[i] >= 10**self.d_digits[i]):
                if(i == 0):
                    raise Exception("Max number of files reached")
                self.d_counts[i - 1] += 1
                self.d_counts[i] = 0
        
    
    """
    return a previously saved version of the bdd or create one if none exist
    """
    def getBDD(self):
        try:
            bdd = pd.read_pickle(self.bdd_path)
        except FileNotFoundError:
            bdd = pd.DataFrame(columns = ['match_id','flipped', 'image_path', 'image_name'] + self.flatInputsDic.column_names + ['output'])
        return bdd
    
    """
    pickle the bdd
    """
    def setbdd(self, bdd):
        bdd.to_pickle(self.bdd_path)
        
    """
    return the tuples(match_id, flipped) already in the bdd
    """
    def getAlreadyComputed(self):
        return set(zip(self.bdd['match_id'],self.bdd['flipped']))
    
    """
    add rows to the bdd
    """
    def addRows(self, match_id, flipped, images, flat_inputs, outputs):
        flat_inputs = np.array(flat_inputs)
        img_pathes = []
        img_names = []
        for image in images:
            img_path, img_name = self.saveImage(image)
            img_pathes.append(img_path)
            img_names.append(img_name)
        dico  = {}
        dico['match_id'] = len(img_pathes) * [match_id]
        dico['flipped'] = len(img_pathes) * [flipped]
        dico['image_path'] = img_pathes
        dico['image_name'] = img_names
        
        for i, col_name in enumerate(self.flatInputsDic.column_names):
            dico[col_name] = flat_inputs[:,i]
            
        dico['output'] = outputs
        
        new_df = pd.DataFrame(dico)
        self.bdd = pd.concat([self.bdd, new_df])
        self.setbdd(self.bdd)
    
    """
    save an image according the current count and return the path and the name of the image
    """
    def saveImage(self, image):
        img_name = ""
        dir_path = self.images_path
        for i,d in enumerate(self.d_counts[:-1]):
            str_d = str(d).zfill(self.d_digits[i])
            dir_path +=str_d + '/'
            img_name += str(d).zfill(self.d_digits[i])
            
        img_name += str(self.d_counts[-1]).zfill(self.d_digits[-1])
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass
        
        img_path = dir_path + '/' + img_name
        with open(img_path, 'wb') as f:
            pickle.dump(image, f)
        self.__addCount()
        return img_path, img_name
    
    """
    return a set of images
    """
    def getImages(self, images_paths):
        total_shape = [len(images_paths)] + list(generalIOLib.MatrixInput().shape)
        images = np.zeros(total_shape, dtype = 'uint8')
        for i,image_path in enumerate(tqdm(images_paths)):
            with open(image_path,'rb') as f:
                images[i] = pickle.load(f)
        return images
    
    """
    plot an image
    """
    def plotImage(self, image_path, image_name = "", output = ""):
        with open(image_path, 'rb') as f:
            image = pickle.load(f)
        colors = ['blue','orange','green','yellow','red','purple','red']
        names = ['filter','encryptor','destructor','ping','emp','scrambler','removal']
        markers = ['o','o','o','8','X','s','x']
        tiles = getTiles()
        
        fig = plt.figure(figsize = (7,7))
        
        ax1 = fig.add_subplot(1,1,1)
        ax1.scatter([x for x,y in tiles],[y for x,y in tiles], color = 'grey', marker = '.')
        for unit_type in range(7):
            X = []
            Y = []
            for v in range(29):
                for u in range(15):
                    if(image[u][v][unit_type]):
                        x,y = generalIOLib.shiftBackTile(u,v)
                        X.append(x)
                        Y.append(y)
            ax1.scatter(X,Y, color = colors[unit_type], marker = markers[unit_type], label = names[unit_type])   
        

        if(output != ""):
            if(output == "stop"):
                ax1.scatter([25],[8],color = "brown", marker = 'o', label = "stop")
            else:
                unit_type,x,y = output.split('_')
                ax1.scatter([int(x)],[int(y)],color = "brown", marker = 'o', label = output)
        
        if(image_name != ""):
            ax1.set_title(image_name)
            
        ax1.legend()
        
        plt.show()
        
