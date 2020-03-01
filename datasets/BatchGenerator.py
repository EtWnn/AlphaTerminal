#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:40:30 2020

@author: etiennew
"""
from multiprocessing import Pool
from itertools import islice
from tqdm import tqdm

import time
import numpy as np
import re
import platform

import sys
sys.path.append('.')

from generalBDDHandler import GeneralBDDHandler
from generalIOLib import GeneralOutputLib

s
class BatchGenerator:
    
    def __init__(self, file_path, batch_size, test_split, validation_split, random_seed = 42):
        np.random.seed(random_seed)
        self.generalBDDHandler = GeneralBDDHandler()
        self.outputLib = GeneralOutputLib()
        self.file_path = file_path
        self.end_file = True
        self.batch_size = batch_size
        self.line_pattern = r'(\d+);(False|True);\(((?:\(\d+, \d+, \d+, \d+\.*\d*\),? ?)*)\);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+\.*\d*);(\d+);((?:\d+_\d+_\d+)|stop)'
        
        self._constructOffsets()
        self._initSetSeparation(test_split, validation_split)
        
        
    """
    itterator that yields the training batches, it prefetch the next batch with thread system
    """
    def getTrainBatches(self, batch_size, shuffle = True):
        if shuffle:
            self.train_index = np.random.permutation(self.train_index)
        n_train_samples = len(self.train_index)
        
        start_index = 0
        end_index = min(n_train_samples, start_index + batch_size)
        
        pool = Pool(processes=1)  
        async_results = pool.apply_async(self._constructAsync2, args = (self.train_index[start_index:end_index],))
        
        while start_index < n_train_samples:
            flat_inputs, images, output_vecs, time_spent = async_results.get()
            infos = {'loading_time': time_spent, 'n_features': end_index - start_index}
            start_index = end_index
            end_index = min(n_train_samples, start_index + batch_size)
            if start_index < n_train_samples:
                async_results = pool.apply_async(self._constructAsync2, args = (self.train_index[start_index:end_index],))
            yield ((flat_inputs, images), output_vecs), infos
        
        pool.close()
        
    """
    itterator that yields the training batches, it prefetch the next batch with thread system
    """
    def getTrainBatches2(self, batch_size, n_workers = 2, shuffle = True):
        if shuffle:
            self.train_index = np.random.permutation(self.train_index)
        n_train_samples = len(self.train_index)
        
        start_index = 0
        end_index = 0
        
        pool = Pool(processes=n_workers)  
        async_results = n_workers * [None]
        
        next_result_index = 0
        n_process_launched = 0
        
        for i in range(n_workers):
            start_index = end_index
            end_index = min(n_train_samples, start_index + batch_size)
            if start_index < n_train_samples:
                async_results[i] = pool.apply_async(self._constructAsync2, args = (self.train_index[start_index:end_index],))
                n_process_launched += 1
                
        
        while n_process_launched:
            flat_inputs, images, output_vecs, time_spent = async_results[next_result_index].get()
            n_process_launched -= 1
            infos = {'loading_time': time_spent, 'n_features': end_index - start_index}
            start_index = end_index
            end_index = min(n_train_samples, start_index + batch_size)
            if start_index < n_train_samples:
                async_results[next_result_index] = pool.apply_async(self._constructAsync2, args = (self.train_index[start_index:end_index],))
                n_process_launched += 1
            next_result_index = (next_result_index + 1) % n_workers
            yield ((flat_inputs, images), output_vecs), infos
        pool.close()
        
    def getRandomValidation(self, batch_size):
        batch_size = min(batch_size, len(self.validation_index))
        index_sample = np.random.permutation(self.validation_index)[:batch_size]
        flat_inputs, images, output_vecs, time_spent = self._constructAsync2(index_sample)
        infos = {'loading_time': time_spent, 'n_features': batch_size}
        return ((flat_inputs, images), output_vecs), infos
        
        
    """
    itterator that yields batches, it prefetch the next batch with thread system
    """
    def getBatches(self):
        pool = Pool(processes=1)  
        async_results = None
        self.end_file = False
        self.current_line = 1 #skip the headers line
        async_results = pool.apply_async(self._constructAsync)
        
        while True:
            try:
                flat_inputs, images, output_vecs, lines_read, time_spent = async_results.get()
                infos = {'loading_time': time_spent, 'n_features': lines_read}
                self.current_line += lines_read
                async_results = pool.apply_async(self._constructAsync)
                yield ((flat_inputs, images), output_vecs), infos
            except StopIteration:
                break
        pool.close()
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
        
        flat_input = np.asarray(row[3:-1], 'float32')
        flat_input_dividers = np.array([30,50,30,30,50,30,100])
        flat_input = flat_input / flat_input_dividers
        
        output = self.outputLib.constructOutput(row[-1])
        
        return (flat_input, image, output)
    
    """
    convert a row (tuple of strings) into flat_inputs, image, output vector
    """
    def convertSample2(self, row, index, flat_inputs, images, output_vecs):
        unit_pattern = r"\((\d+), (\d+), (\d+), (\d+\.*\d*)\)"
        units_list = []
        units_search = re.findall(unit_pattern, row[2])
        for x,y,unit_type, stability in units_search:
            units_list.append((int(x), int(y), int(unit_type), float(stability)))
            
        self.generalBDDHandler.fillImage(images[index], units_list)
        
        flat_input = np.asarray(row[3:-1], 'float32')
        flat_input_dividers = np.array([30,50,30,30,50,30,100])
        flat_input = flat_input / flat_input_dividers
        
        self.outputLib.fillOutput(output_vecs[index], row[-1])
    
    """
    contruct the list of the lines' offsets to read the file faster
    """
    def _constructOffsets(self):
        offset = 0
        self.lines_offsets = []
        with open(self.file_path) as file:
            for line in tqdm(file, desc = "lines offset reading"):
                if platform.system() == 'Windows':
                    self.lines_offsets.append(offset)
                    offset += len(line) + 1
                elif platform.system() == 'Linux' or platform.system() == 'Darwin':
                    self.lines_offsets.append(offset+1)
                    offset += len(line)
                else:
                    raise ValueError(f"unknown system {platform.system()}")
        self.lines_offsets = tuple(self.lines_offsets)

    """
    initialise the random train/validation/test separations
    """    
    def _initSetSeparation(self, test_split, validation_split):
        self.n_samples = len(self.lines_offsets)-1
        random_permutation = np.random.permutation(self.n_samples)
        n_test_index = int(test_split * self.n_samples)
        n_validation_index = int(validation_split * (self.n_samples - n_test_index))
        n_train_index = self.n_samples - n_validation_index - n_test_index
        self.train_index = random_permutation[:n_train_index]
        self.validation_index = random_permutation[n_train_index : n_train_index + n_validation_index]
        self.test_index = random_permutation[n_train_index + n_validation_index: n_train_index + n_validation_index + n_test_index]
        
    """
    construct a batch
    """    
    def _constructAsync2(self, lines_index):
        t0 = time.time()
        file = open(self.file_path, 'r')
        lines_index.sort()
        n_lines = len(lines_index)
        flat_inputs = np.zeros((n_lines, 7), dtype = 'float32')
        images = np.zeros((n_lines, 15, 29, 7 ), dtype = 'float32')
        output_vecs = np.zeros((n_lines, 925), dtype = 'float32')
        for i, index in enumerate(lines_index):
            file.seek(self.lines_offsets[index+1]) #+1 because of the headers' row
            line = file.readline()
            samples = re.findall(self.line_pattern, line)
            try:
                self.convertSample2(samples[0], i, flat_inputs, images, output_vecs)
            except Exception as e:
                print(f"error :{e}, line:{line}, index:{index}, offset:{self.lines_offsets[index+1]}")
                raise e
        return flat_inputs, images, output_vecs, time.time() - t0
    
    """
    construct a batch
    """    
    def _constructAsync(self):
        t0 = time.time()
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
            return np.asarray(flat_inputs,'float32'), np.asarray(images,'float32'), np.asarray(output_vecs,'float32'), lines_read, time.time() - t0
        else:
            raise StopIteration()
    

