# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""
import logging
import utils
import settings
import time
import csv
import random
from nk import sim, model

runConfigs = [  
#                [sim.SearchMethod.STEEPEST, 2, False],
#                [sim.SearchMethod.STEEPEST, 2, False],
#                [sim.SearchMethod.STEEPEST, 1, False],
#                [sim.SearchMethod.STEEPEST, 1, True],
#                [sim.SearchMethod.GREEDY, 2, True],
#                [sim.SearchMethod.STEEPEST, 2, False],
#                [sim.SearchMethod.GREEDY, 1, False],
                [sim.SearchMethod.RANDOMTHENSTEEPEST, 2, True]
            ]
random.seed(utils.getDefaultSeedObject())
utils.setupLogging();

results = []
resFile = open(settings.RESULTS_CSV_FILE, 'a')
resWriter = csv.writer(resFile)
header = ["N", "K", "Fitness", "SearchMethod", "Distance", "CumulativeDistance", "NumberOfLandscapes", "StdDevFitness", "AttemptedFlips", "AcceptedFlips"]
resWriter.writerow(header)
logger =  logging.getLogger(__name__)
landscapes = settings.landscapes
for nVal in settings.nList:
    for kVal in settings.kList:
        if kVal <= nVal:
            if kVal == nVal:
                realK = kVal-1
            else:
                realK = kVal
            for [search, distance, cum] in runConfigs:
                params = sim.SimInput(nVal, realK)
                params.setSearchMethod(search)
                params.setMutateDistance(distance)
                params.setCumulativeDistance(cum)
                params.generateAdjMatrix()
    
                utils.logInitialConditions(logger, params, landscapes)
    
                simulation = model.NK(params)
                key = int(round(time.time() * 1000))
                output = simulation.runSimulation(key, landscapes)
    
                utils.logResults(logger, params, output, landscapes)
    
                nextRow = []
                nextRow.append(params.nValue())
                nextRow.append(params.kValue())
                nextRow.append(output.meanFitness())
                nextRow.append(params.searchMethodString())
                nextRow.append(params.mutateDistance())
                nextRow.append(params.cumulativeDistance())
                nextRow.append(output.landscapes())
                nextRow.append(output.stddevFitness())
                nextRow.append(output.meanAttemptedFlips())
                nextRow.append(output.meanAcceptedFlips())
                resWriter.writerow(nextRow)
                resFile.flush()
                results.append([params, output])
                
                params = None
                simulation = None
                output = None
                utils.logLine(logger)

resFile.close()