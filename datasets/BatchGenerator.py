#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:40:30 2020

@author: etiennew
"""
from multiprocessing import Pool
from itertools import islice
import time
import numpy as np
import re
from tqdm import tqdm

import sys
sys.path.append('.')

from generalBDDHandler import GeneralBDDHandler
from generalIOLib import GeneralOutputLib

class BatchGenerator:
    
    def __init__(self, file_path, batch_size, train_split, random_seed = 42):
        np.random.seed(random_seed)
        self.generalBDDHandler = GeneralBDDHandler()
        self.outputLib = GeneralOutputLib()
        self.file_path = file_path
        self.end_file = True
        self.batch_size = batch_size
        self.train_size = int(self.batch_size * train_split)
        train_index = np.random.permutation(self.batch_size)[:self.train_size]
        self.is_train = [(i in train_index) for i in range(batch_size)]
        self.line_pattern = r'(\d+);(False|True);\(((?:\(\d+, \d+, \d+, \d+\.*\d*\),? ?)*)\);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+);((?:\d+_\d+_\d+)|stop)'
        
    
    """
    itterator that yields batches, it prefetch the next batch with thread system
    """
    def getBatches(self):
        pool = Pool(processes=2)  
        current_result = 0
        async_results = [None, None]
        self.end_file = False
        self.current_line = 1 #skip the headers line
        async_results[0] = pool.apply_async(self._constructAsync)
        while not(async_results[0].ready()): #wait for the first result to be finished
            time.sleep(0.1)
        
        while True:
            try:
                flat_inputs, images, output_vecs, lines_read = async_results[current_result].get()
                self.current_line += lines_read
                async_results[1 - current_result] = pool.apply_async(self._constructAsync)
                yield flat_inputs, images, output_vecs
                current_result = 1 - current_result
            except StopIteration:
                break
    
    """
    convert a row (tuple of strings) into flat_inputs, image, output vector
    """
    def convertSample(self, row):
        unit_pattern = r"\((\d+), (\d+), (\d+), (\d+\.*\d*)\)"
        units_list = []
        units_search = re.findall(unit_pattern, row[2])
        for x,y,unit_type, stability in units_search:
            units_list.append((int(x), int(y), int(unit_type), float(stability)))
        image = self.generalBDDHandler.getImage(units_list)
        
        flat_input = np.asarray(row[3:-1], 'float')
        
        output = self.outputLib.constructOutput(row[-1])
        
        return (flat_input, image, output)
    
    """
    construct a batch
    """    
    def _constructAsync(self):
        file = open(self.file_path)
        itterator = islice(file, self.current_line, None)
        lines_read = 0
        flat_inputs = []
        images = []
        output_vecs = []
        while lines_read < self.batch_size and not(self.end_file):
            try:
                line = next(itterator)
                samples = re.findall(self.line_pattern, line)
                flat_input, image, output_vec = self.convertSample(samples[0])
                flat_inputs.append(flat_input)
                images.append(image)
                output_vecs.append(output_vec)
                lines_read +=1
            except StopIteration:
                self.end_file = True
        file.close()
        if flat_inputs != []:
            return np.asarray(flat_inputs,'float'), np.asarray(images,'float'), np.asarray(output_vecs,'float'), lines_read
        else:
            raise StopIteration()
            
# if __name__ == '__main__':
#     batch_generator = BatchGenerator('datasets/generalIO_v2.csv',1024,1,42)
#     for b in batch_generator.getBatches():
#         print('got one')
#         break