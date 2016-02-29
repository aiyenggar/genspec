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
import datetime
import matplotlib.pyplot as plt
from nk import sim, model

runConfigs = [  
                [sim.SearchMethod.STEEPEST, 2, True, 5],
                [sim.SearchMethod.STEEPEST, 1, True, 15]
            ]

def getDictFitness(fitList, dictIndex):
    if len(fitList) == 0:
        return None # This is an error
    if (dictIndex < len(fitList)):
        return fitList[dictIndex]
    return fitList[len(fitList)-1]
        
            
random.seed(utils.getDefaultSeedObject())
utils.setupLogging();
colors = "bkmrg"
linestyle = ["-", "-.", "--", "--", "-"]
linewidth = [2, 3, 2, 3, 2]
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
            maxTimePeriod = 0
            transWriter = None
            transactionCSVFile = None
            while len(params) <= len(runConfigs):
                params.append(None)
                fitnessDistribution.append([])
                attemptedFlipsDist.append([])
                acceptedFlipsDist.append([])
                periodFitnessDist.append([])
                tickLog.append({})
                savedNodeConfig = None
                savedFitnessDict = None
            for iteration in range(0, landscapes):
                """ Force a new Landscape creation """
                if (iteration%landscapes == 0):
                    savedNodeConfig = None
                    savedFitnessDict = None
                configIndex = 0
                dummy = sim.SimInput(nVal, realK)
                dummy.generateAdjMatrix()
                iterationAdjMatrix = dummy.adjMatrix()
                dummy = None
                for [search, distance, cum, nBar] in runConfigs:
                    if (params[configIndex] == None):
                        params[configIndex] = sim.SimInput(nVal, realK)
                        params[configIndex].setSearchMethod(search)
                        params[configIndex].setMutateDistance(distance)
                        params[configIndex].setCumulativeDistance(cum)
                        params[configIndex].setNBar(nBar)
                        
                    params[configIndex].setAdjMatrix(iterationAdjMatrix)
                    
                    if (savedFitnessDict != None and savedNodeConfig != None):
                        params[configIndex].setStartConfig(savedNodeConfig, savedFitnessDict)
                    else:
                        params[configIndex].clearStartConfig()
                        # Do you need to initialise the startConfig?
                    utils.logInitialConditions(logger, params[configIndex], landscapes)
        
                    simulation = model.NK(params[configIndex])
                    """ Save the nodeConfig for use in following iteration """
                    savedNodeConfig = simulation.nodeConfig()
#                    header = ["Fields", "Key", "N", "K", "A", "SearchMethod", "Distance", "CumulativeDistance"]
#                    header += ["Landscape", "NumberOfLandscapes", "AttemptedFlips", "AcceptedFlips", "WasFlipAccepted"]
#                    header += ["CurrentConfiguration", "CurrentSystemFitness", "ConsideredConfiguration"]
#                    for i in range(0, nVal):
#                        header.append("w" + str(i))
#                    header.append("ConsideredSystemFitness")
 
                    key = int(round(time.time() * 1000))
                    
#                    transactionCSVFile = open("log/" + str(iteration) + str(configIndex) + ".csv", 'w')
#                    transWriter = csv.writer(transactionCSVFile)
#                    transWriter.writerow(header)
   
                    [f, at, ac] = simulation.run(key, iteration, transWriter)
                    fitnessDistribution[configIndex].append(f)
                    attemptedFlipsDist[configIndex].append(at)
                    acceptedFlipsDist[configIndex].append(ac)
                    tickLog[configIndex][iteration] = simulation.attLog()
                    if len(tickLog[configIndex][iteration]) > maxTimePeriod:
                        maxTimePeriod = len(tickLog[configIndex][iteration])
                        
                    """ Save the fitnessDict for use in following iteration """
                    
                    savedFitnessDict = simulation.fitnessDict()
                    if transactionCSVFile != None:
                        transactionCSVFile.close()
                    configIndex += 1
            
            if maxTimePeriod > 100:
                div100 = int(maxTimePeriod * 3/400) 
                maxTimePeriod = int(div100 * 100)
            output = []    
            plt.figure(figsize=(15,24))    
            plt.xlabel("Time Period")
            plt.ylabel("Fitness")
            ax = plt.subplot(len(settings.kList) * len(settings.nList), 1, plotId)

            """ Calculate the time periodwise average system fitness """
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
                
                fileString = "N" + str(nVal) + "-K" + str(realK) + "-L" + str(landscapes) + "-D" + str(params[configIndex].mutateDistance()) + "-" + params[configIndex].searchMethodString() + "-" + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + ".csv"
                tickFile = open("log/" + fileString, 'w')
                tickWriter = csv.writer(tickFile)
                tickWriter.writerow(periodFitnessDist[configIndex])
                tickFile.close()
                existingLen = len(periodFitnessDist[configIndex])
                shortage = maxTimePeriod - existingLen
                if shortage > 0:
                    addOn = [periodFitnessDist[configIndex][existingLen-1]] * shortage
                    periodFitnessDist[configIndex] += addOn
                periodFitnessDist[configIndex] = periodFitnessDist[configIndex][0:maxTimePeriod]

                ax.plot(range(1, len(periodFitnessDist[configIndex])+1), 
                              periodFitnessDist[configIndex], color=colors[configIndex],
                              label=str(params[configIndex].mutateDistance()) + " " + params[configIndex].searchMethodString() + " (" + str(round(output[configIndex].meanFitness(),4)) +")",
                              lw=linewidth[configIndex], ls=linestyle[configIndex]
                        )
                ax.legend(fancybox=True, shadow=True, ncol=1, loc='lower right')
                plt.title("N = " + str(nVal) + " K = " + str(realK) + " Landscapes = " + str(landscapes))

            plotId += 1
            plt.show()
            utils.logLine(logger)

resFile.close()