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
import numpy
import matplotlib.pyplot as plt
from nk import sim, model

runConfigs = [  
                [sim.SearchMethod.GREEDY, 2, True],
                [sim.SearchMethod.STEEPEST, 2, True],
                [sim.SearchMethod.RANDOMTHENSTEEPEST, 2, True],
                [sim.SearchMethod.GREEDY, 1, True],
                [sim.SearchMethod.STEEPEST, 1, True],
            ]

def getDictFitness(fitList, dictIndex):
    if len(fitList) == 0:
        return None # This is an error
    if (dictIndex < len(fitList)):
        return fitList[dictIndex]
    return fitList[len(fitList)-1]
        
            
random.seed(utils.getDefaultSeedObject())
utils.setupLogging();

results = []
resFile = open(settings.RESULTS_CSV_FILE, 'a')
resWriter = csv.writer(resFile)
resultHeader = ["N", "K", "Fitness", "SearchMethod", "Distance", "CumulativeDistance", "NumberOfLandscapes", "StdDevFitness", "AttemptedFlips", "AcceptedFlips"]
resWriter.writerow(resultHeader)
logger =  logging.getLogger(__name__)
landscapes = settings.landscapes
plotId = 1
for nVal in settings.nList:
    for kVal in settings.kList:
        if kVal <= nVal:
            if kVal == nVal:
                realK = kVal-1
            else:
                realK = kVal
            fitnessDistribution = []
            attemptedFlipsDist = []
            acceptedFlipsDist = []
            periodFitnessDist = []
            tickLog = []
            params = []
            while len(params) <= len(runConfigs):
                params.append(None)
                fitnessDistribution.append([])
                attemptedFlipsDist.append([])
                acceptedFlipsDist.append([])
                periodFitnessDist.append([])
                tickLog.append({})
            for iteration in range(0, landscapes):
                """ Force a new Landscape creation """
                savedNodeConfig = None
                savedFitnessDict = None
                configIndex = 0
                dummy = sim.SimInput(nVal, realK)
                dummy.generateAdjMatrix()
                iterationAdjMatrix = dummy.adjMatrix()
                dummy = None
                for [search, distance, cum] in runConfigs:
                    if (params[configIndex] == None):
                        params[configIndex] = sim.SimInput(nVal, realK)
                        params[configIndex].setSearchMethod(search)
                        params[configIndex].setMutateDistance(distance)
                        params[configIndex].setCumulativeDistance(cum)
                        
                    params[configIndex].setAdjMatrix(iterationAdjMatrix)
                    
                    if (savedFitnessDict != None and savedNodeConfig != None):
                        params[configIndex].setStartConfig(savedNodeConfig, savedFitnessDict)
                    else:
                        params[configIndex].clearStartConfig()
                        # Do you need to initialise the startConfig?
                    utils.logInitialConditions(logger, params[configIndex], landscapes)
        
                    simulation = model.NK(params[configIndex])
                    savedNodeConfig = simulation.nodeConfig()
                    header = ["Fields", "Key", "N", "K", "A", "SearchMethod", "Distance", "CumulativeDistance"]
                    header += ["Landscape", "NumberOfLandscapes", "AttemptedFlips", "AcceptedFlips", "WasFlipAccepted"]
                    header += ["CurrentConfiguration", "CurrentSystemFitness", "ConsideredConfiguration"]
                    for i in range(0, nVal):
                        header.append("w" + str(i))
                    header.append("ConsideredSystemFitness")
 
                    key = int(round(time.time() * 1000))
                    
                    transactionCSVFile = open("log/" + str(iteration) + str(configIndex) + ".csv", 'w')
                    transWriter = csv.writer(transactionCSVFile)
                    transWriter.writerow(header)
   
                    [f, at, ac] = simulation.run(key, iteration, transWriter)
                    fitnessDistribution[configIndex].append(f)
                    attemptedFlipsDist[configIndex].append(at)
                    acceptedFlipsDist[configIndex].append(ac)
                    tickLog[configIndex][iteration] = simulation.attLog()
                    """ Save the nodeConfig and fitnessDict for use in following iteration """
                    
                    savedFitnessDict = simulation.fitnessDict()
                    transactionCSVFile.close()
                    configIndex += 1
            
            plt.figure(figsize=(12,24))            
            ax = plt.subplot(len(settings.kList) * len(settings.nList), 1, plotId)

            """ Calculate the time periodwise average system fitness """
            for configIndex in range(0, len(runConfigs)): 
                tickDict = tickLog[configIndex]
                maxLen = 0
                for nextKey in tickDict:
                    nextLen = len(tickDict[nextKey])
                    if nextLen > maxLen:
                        maxLen = nextLen
                
                dictIndex = 0
                while dictIndex < maxLen:
                    sum = 0
                    for nextKey in tickDict:
                        fitList = tickDict[nextKey]
                        nextFitness = getDictFitness(fitList, dictIndex)
                        sum += nextFitness
                    avgFitness = sum/len(tickDict)
                    # landscapes should be the same as len(tickDict)
                    periodFitnessDist[configIndex].append(avgFitness)
                    dictIndex += 1
                colors = "bkmrg"
                linestyle = ["-", "-.", "--", "--", "-"]
                linewidth = [2, 3, 2, 3, 2]
                plt.xlabel("Time Period")
                plt.ylabel("Fitness")
                maxLen = 899
                periodFitnessDist[configIndex] = periodFitnessDist[configIndex][0:maxLen]
                existingLen = len(periodFitnessDist[configIndex])
                shortage = maxLen + 1 - existingLen
                addOn = [periodFitnessDist[configIndex][existingLen-1]] * shortage
                periodFitnessDist[configIndex] += addOn
                ax.plot(range(1, len(periodFitnessDist[configIndex])+1), 
                                          periodFitnessDist[configIndex], 
                                          color=colors[configIndex],
                                          label=params[configIndex].searchMethodString() + " " + str(params[configIndex].mutateDistance()),
                                          lw=linewidth[configIndex],
                                          ls=linestyle[configIndex]
                                            )
                ax.legend(fancybox=True, shadow=True, ncol=1, loc='best')
                plt.title("N = " + str(nVal) + " K = " + str(kVal) + " Landscapes = " + str(landscapes))

            plotId += 1
            plt.show()
                
            output = []               
            for configIndex in range(0, len(runConfigs)):                     
                tempo = sim.SimOutput()
                tempo.setLandscapes(landscapes)
                tempo.setFinessDistribution(fitnessDistribution[configIndex])
                tempo.setAttemptedFlipsDistribution(attemptedFlipsDist[configIndex])
                tempo.setAcceptedFlipsDistribution(acceptedFlipsDist[configIndex])
                output.append(tempo)
                utils.logResults(logger, params[configIndex], tempo, landscapes)
            
                nextRow = []
                nextRow.append(params[configIndex].nValue())
                nextRow.append(params[configIndex].kValue())
                nextRow.append(output[configIndex].meanFitness())
                nextRow.append(params[configIndex].searchMethodString())
                nextRow.append(params[configIndex].mutateDistance())
                nextRow.append(params[configIndex].cumulativeDistance())
                nextRow.append(output[configIndex].landscapes())
                nextRow.append(output[configIndex].stddevFitness())
                nextRow.append(output[configIndex].meanAttemptedFlips())
                nextRow.append(output[configIndex].meanAcceptedFlips())
                resWriter.writerow(nextRow)
                resFile.flush()
                results.append([params[configIndex], output[configIndex]])
            utils.logLine(logger)

resFile.close()