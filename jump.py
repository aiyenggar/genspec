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
                [sim.SearchMethod.GREEDY, 2, True],
#                [sim.SearchMethod.STEEPEST, 2, True],
#                [sim.SearchMethod.RANDOMTHENSTEEPEST, 2, True]
            ]
#random.seed(utils.getDefaultSeedObject())
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
                header = ["Fields", "Key", "N", "K", "A", "SearchMethod", "Distance", "CumulativeDistance"]
                header += ["Landscape", "NumberOfLandscapes", "AttemptedFlips", "AcceptedFlips", "WasFlipAccepted"]
                header += ["CurrentConfiguration", "CurrentSystemFitness", "ConsideredConfiguration"]
                for i in range(0, nVal):
                    header.append("w" + str(i))
                header.append("ConsideredSystemFitness")
                
                transactionCSVFile = open(settings.TRANSACTION_CSV_FILE, 'a')
                transWriter = csv.writer(transactionCSVFile)
                transWriter.writerow(header)
                fitnessDistribution = []
                attemptedFlipsDist = []
                acceptedFlipsDist = []
                output = sim.SimOutput()

                key = int(round(time.time() * 1000))
                for iteration in range(0, landscapes):
                    [f, at, ac] = simulation.run(key, iteration, transWriter)
                    fitnessDistribution.append(f)
                    attemptedFlipsDist.append(at)
                    acceptedFlipsDist.append(ac)
                
                output.setLandscapes(landscapes)
                output.setFinessDistribution(fitnessDistribution)
                output.setAttemptedFlipsDistribution(attemptedFlipsDist)
                output.setAcceptedFlipsDistribution(acceptedFlipsDist)
                utils.logResults(logger, params, output, landscapes)
                transactionCSVFile.close()
                
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