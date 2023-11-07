#!/usr/bin/env python
# coding: utf-8

import re
import os
import json
import numpy as np
from tqdm import tqdm
import multiprocessing as mp
from datetime import datetime
from utils import * # TODO: replace with a safer import

def processData(numSamples, nv, decimals, 
                template, dataPath, fileID, time, 
                numberofPoints=[20,250],
                xRange=[-3,3], 
                op_list=["exp"],
                numSamplesEachEq=1,
                threshold=100):

    for i in tqdm(range(numSamples)):
        structure = template.copy()
        
        # Generate the 'exp()' equation
        skeletonEqn = "exp(x1)"

        for e in range(numSamplesEachEq):
            # Replace the constants with new ones
            cleanEqn = skeletonEqn
            
            # Generate new data points
            nPoints = np.random.randint(*numberofPoints)

            try:
                data = generateDataStrEq(cleanEqn, n_points=nPoints, n_vars=nv,
                                         decimals=decimals, min_x=xRange[0], max_x=xRange[1])
            except: 
                # For different reasons, this might happen, including but not limited to division by zero
                continue

            # Use the new x and y
            x, y = data

            # Check if there are nan/inf/very large numbers in the y
            if np.isnan(y).any() or np.isinf(y).any():
                # Repeat the data generation
                e -= 1
                continue
                
            # Replace out-of-threshold values with maximum numbers
            y = [e if abs(e) < threshold else np.sign(e) * threshold for e in y]

            if len(y) == 0:
                print('Empty y, x: {}, most of the time this is because of wrong numberofPoints: {}'.format(x, numberofPoints))
                e -= 1
                continue

            # Just make sure there are no samples out of the threshold
            if abs(min(y)) > threshold or abs(max(y)) > threshold:
                raise 'Err: Min:{}, Max:{}, Threshold:{}, \n Y:{} \n Eq:{}'.format(min(y), max(y), threshold, y, cleanEqn)

            # Hold data in the structure
            structure['X'] = list(x)
            structure['Y'] = y
            structure['Skeleton'] = skeletonEqn
            structure['EQ'] = cleanEqn

            outputPath = dataPath.format(fileID, nv, time)
            if os.path.exists(outputPath):
                fileSize = os.path.getsize(outputPath)
                if fileSize > 500000000:  # 500 MB
                    fileID += 1 
            with open(outputPath, "a", encoding="utf-8") as h:
                json.dump(structure, h, ensure_ascii=False)
                h.write('\n')

def main():
   # Config
    seed = 2023
    import random
    random.seed(seed)
    np.random.seed(seed=seed)  # Fix the seed for reproducibility

    numVars = [1]  # Number of variables (in this case, just 'x')
    decimals = 8
    numberofPoints = [30, 31]
    numSamples = 100
    folder = './Dataset'
    dataPath = folder + '/{}_{}_{}.json'

    xRange = [-3, 3]
    numSamplesEachEq = 50
    threshold = 5000

    op_list = ["exp"]

    print(os.mkdir(folder) if not os.path.isdir(folder) else 'The path already exists!')

    template = {'X': [], 'Y': 0.0, 'EQ': ''}
    fileID = 0
    processes = []
    for i, nv in enumerate(numVars):
        now = datetime.now()
        time = '{}_'.format(i) + now.strftime("%d%m%Y_%H%M%S")
        print('Processing equations with {} variables!'.format(nv))

        p = mp.Process(target=processData, 
                       args=(numSamples, nv, decimals, template, 
                             dataPath, fileID, time, numberofPoints, xRange, op_list,
                             numSamplesEachEq, threshold)
                      )
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
