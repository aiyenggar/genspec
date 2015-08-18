# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:37:01 2015

@author: aiyenggar
"""
import logging
import scipy
import math
import csv
import settings

from nk import sim

def listString(configuration):
    pString = ""
    for element in configuration:
        pString += str(element)
    return pString

class NK:
    def __init__(self, simInput):
        self.__inputs = simInput
        self.__nodeConfig = None
        self.__fitnessDict = None
        self.logger =  logging.getLogger(__name__)

    def setup(self):
        self.__nodeConfig = list([])
        self.__fitnessDict = dict({})
        self.__attemptedFlips = 0
        self.__acceptedFlips = 0
        for index in range(0, self.__inputs.nValue()):
            nextNodeValue = sim.getRandomInt(0, self.__inputs.aValue()-1)
            self.__nodeConfig.append(nextNodeValue)
            self.__fitnessDict[index] = dict({})


    def getMaskedConfig(self, nodeIndex, configuration):
        """
        Given the node index and node configuration return
        a tuple that is the masked configuration
        """
        maskedConfig = list(configuration)
        hashKey = ()
        colValue = 0
        for kValue in self.__inputs.adjMatrix()[nodeIndex]:
            if kValue == 0:
                maskedConfig[colValue] = self.__inputs.aValue()
            colValue += 1
        hashKey = tuple(maskedConfig)
        return hashKey

    def updateNodeContribution(self, nodeIndex, configuration):
        """
        Given the the node index and new node configuration,
        update the node fitness contributions

        Parameters
        ----------
        nodeIndex   : number
                    index of the node whose fitness contribution has changed
        configuration: list
                    current node configuration

        Returns
        -------
        None

        Example
        -------
        """

        hashKey = self.getMaskedConfig(nodeIndex, configuration)
        if hashKey not in self.__fitnessDict[nodeIndex]:
            self.__fitnessDict[nodeIndex][hashKey] = sim.getRandom()
        return self.__fitnessDict[nodeIndex][hashKey]

    def refreshFitnessContributions(self, newConfig, prevConfig=None):
        if prevConfig != None:
            # Find nodes that have changed between prevConfig and newConfig
            pass
        maxConfig = self.__inputs.aValue() ** (self.__inputs.kValue() + 1)
        nextNode = 0
        while nextNode < self.__inputs.nValue():
            if len(self.__fitnessDict[nextNode]) < maxConfig:
                self.updateNodeContribution(nextNode, newConfig)
            nextNode += 1

    def getFitness(self, configuration):
        runningFitnessSum = 0.0
        for index in range(0, self.__inputs.nValue()):
            runningFitnessSum += self.updateNodeContribution(index, configuration)
        return runningFitnessSum/self.__inputs.nValue()

    def getRandam1HDMutant(self, configuration, avoidNodes={}):
        randomNode = sim.getRandomInt(0, self.__inputs.nValue()-1, avoidNodes)
        randomAllele = sim.getRandomInt(0, self.__inputs.aValue()-1)
        # Find an Allele at position randomNode that is different
        while randomAllele == configuration[randomNode]:
            randomAllele = sim.getRandomInt(0, self.__inputs.aValue()-1)
        randomConfig = list(configuration)
        randomConfig[randomNode] = randomAllele
        return [randomNode, randomConfig]


    def getJumpNeighbour(self, configuration, distance, cumulative):
        """
        When cumulative is True a random distance in [1, distance] is chosen
        and a configuration at that random distance is generated 
        When cumulative is False a configuration at exactly distance is generated
        """
        nodesMutated = {}
        current = configuration
        if cumulative == True:
            generatedDistance = sim.getRandomInt(1, distance)
        else:
            generatedDistance = distance
            
        for index in range(0, generatedDistance):
            [nextNode, nextConfig] = self.getRandam1HDMutant(current, nodesMutated)
            nodesMutated[nextNode] = 1
            current = nextConfig
        return current

    def getNeighbours(self, configuration, distance=1):
        """
        Generate all node configurations that are at a given
        hamming distance from the given node configuration
        """
        allNodes = []
        nextLevel = []
        nextLevel.append(tuple(configuration))
        allNodes.append(set(nextLevel))
        for index in range(0, distance):
            nextLevel = []
            for popConfig in allNodes[index]:
                nextLevel.extend(self.get1HDNeighbours(popConfig))
            allNodes.append(set(nextLevel))
        allNeighbours = set([])
        for index in range(0, distance):
            allNeighbours = allNeighbours.union(allNodes[index+1])
        allNeighbours.remove(tuple(configuration))
        return list(allNeighbours)

    def get1HDNeighbours(self, configuration):
        """
        Generate all node configurations that are at 1 (one)
        hamming distance from the given configuration
        """
        listNeighbours = []
        nextNode = 0
        while (nextNode < self.__inputs.nValue()):
            nextAllele = 0
            while (nextAllele < self.__inputs.aValue()):
                if (nextAllele != configuration[nextNode]):
                    nextNeighbour = list(configuration)
                    nextNeighbour[nextNode] = nextAllele
                    listNeighbours.append(tuple(nextNeighbour))
                nextAllele += 1
            nextNode += 1
        return listNeighbours

    def nodeContriString(self, configuration):
        pString = ""
        for index in range(0, self.__inputs.nValue()):
            hashKey = self.getMaskedConfig(index, configuration)
            pString += str(round(self.__fitnessDict[index][hashKey], self.__inputs.precision()))
            if index != (self.__inputs.nValue() - 1):
                pString += ", "
        return pString

    def logState(self, configuration, fitness, leadingString=""):
        pString = leadingString + listString(configuration) + " | "
        pString += self.nodeContriString(configuration) + " | "
        pString += str(round(fitness, self.__inputs.precision()))
        self.logger.info(pString)

    def getMaxNeighbours(self):
        maxNeighbours = 0
        if self.__inputs.cumulativeDistance() == True:
            startDistance = 0
        else:
            startDistance = self.__inputs.mutateDistance() - 1
        for distance in range(startDistance, self.__inputs.mutateDistance()):
            combinations = scipy.misc.comb(self.__inputs.nValue(), distance+1)
            variations = math.pow(self.__inputs.aValue()-1, distance+1)
            maxNeighbours += combinations * variations
        return maxNeighbours

    def getDefaultStatsList(self, keyVal, countLandscapes, iteration):
        fields = []
        fields.append(0)
        fields.append(keyVal)
        fields.append(self.__inputs.nValue())
        fields.append(self.__inputs.kValue())
        fields.append(self.__inputs.aValue())
        fields.append(self.__inputs.searchMethodString())
        fields.append(self.__inputs.mutateDistance())
        fields.append(self.__inputs.cumulativeDistance())
        fields.append(iteration)
        fields.append(countLandscapes)
        fields[0] = len(fields)
        return fields
        
    def updateStatsListFlips(self, fields, attemptedFlips, acceptedFlips, wasFlipAccepted):
        fields.append(attemptedFlips)
        fields.append(acceptedFlips)
        fields.append(wasFlipAccepted)
        fields[0] = len(fields)
        return fields 

    def updateStatsListCurrent(self, fields, currentConfig, currentFitness):
        fields.append(listString(currentConfig))
        fields.append(currentFitness)
        fields[0] = len(fields)
        return fields
        
    def updateStatsListConsidered(self, fields, consideredConfig, consideredFitness):
        fields.append(listString(consideredConfig))
        for j in range(0, self.__inputs.nValue()):
            hashKey = self.getMaskedConfig(j, consideredConfig)
            fields.append(round(self.__fitnessDict[j][hashKey], self.__inputs.precision()))
        fields.append(consideredFitness)
        fields[0] = len(fields)
        return fields

    def searchNext(self, nodeConfig, nodeFitness, transWriter, keyVal, countLandscapes, iteration):
        transStats = self.getDefaultStatsList(keyVal, countLandscapes, iteration)
        selectedConfig = nodeConfig
        selectedFitness = nodeFitness
        if (self.__inputs.searchMethod() == sim.SearchMethod.STEEPEST):
            neighbours = self.getNeighbours(nodeConfig, self.__inputs.mutateDistance())
            for adjConfig in neighbours:
                transStats = self.getDefaultStatsList(keyVal, countLandscapes, iteration)
                self.__attemptedFlips += 1
                self.refreshFitnessContributions(adjConfig, nodeConfig)
                systemFitness = self.getFitness(adjConfig)
                self.logState(adjConfig, systemFitness, "\t")
                
                if (systemFitness > selectedFitness):
                    flag = 1
                    self.__acceptedFlips += 1
                else:
                    flag = 0
                transStats = self.updateStatsListFlips(transStats, self.__attemptedFlips,
                                          self.__acceptedFlips, flag)
                transStats = self.updateStatsListCurrent(transStats, selectedConfig, selectedFitness)
                transStats = self.updateStatsListConsidered(transStats, adjConfig, systemFitness)
                transWriter.writerow(transStats)
                if (flag == 1):
                    selectedConfig = list(adjConfig)
                    selectedFitness = systemFitness
            return [selectedConfig, selectedFitness]
        elif (self.__inputs.searchMethod() == sim.SearchMethod.GREEDY):          
            exploredNeighbours = {}
            maxNeighbours = self.getMaxNeighbours()
            while len(exploredNeighbours) < maxNeighbours:
                transStats = self.getDefaultStatsList(keyVal, countLandscapes, iteration)
                randomConfig = self.getJumpNeighbour(nodeConfig, 
                                                     self.__inputs.mutateDistance(), 
                                                     self.__inputs.cumulativeDistance()
                                                     )
                self.__attemptedFlips += 1
                hashKey = tuple(randomConfig)
                if hashKey not in exploredNeighbours:
                    exploredNeighbours[hashKey] = 1
                    # This is a configuration we have not seen before, so compute the fitness contributions
                    self.refreshFitnessContributions(randomConfig, nodeConfig)
                else:
                    exploredNeighbours[hashKey] += 1             
                systemFitness = self.getFitness(randomConfig)
                self.logState(randomConfig, systemFitness, "\t")

                if (systemFitness > selectedFitness):
                    flag = 1
                    self.__acceptedFlips += 1
                else:
                    flag = 0
                transStats = self.updateStatsListFlips(transStats, self.__attemptedFlips,
                                          self.__acceptedFlips, flag)
                transStats = self.updateStatsListCurrent(transStats, selectedConfig, selectedFitness)
                transStats = self.updateStatsListConsidered(transStats, randomConfig, systemFitness)
                transWriter.writerow(transStats)       
                if flag == 1:
                    selectedConfig = list(randomConfig)
                    selectedFitness = systemFitness
                    return [selectedConfig, selectedFitness]
            return [selectedConfig, selectedFitness]
        else:
            return None


    def runSimulation(self, keyVal, countLandscapes):
        header = ["Fields", "Key", "N", "K", "A", "SearchMethod", "Distance", "CumulativeDistance"]
        header += ["Landscape", "NumberOfLandscapes", "AttemptedFlips", "AcceptedFlips", "WasFlipAccepted"]
        header += ["CurrentConfiguration", "CurrentSystemFitness", "ConsideredConfiguration"]
        for i in range(0, self.__inputs.nValue()):
            header.append("w" + str(i))
        header.append("ConsideredSystemFitness")
                
        transactionCSVFile = open(settings.TRANSACTION_CSV_FILE, 'w')
        transWriter = csv.writer(transactionCSVFile, dialect='excel')
        transWriter.writerow(header)
        outputs = sim.SimOutput()
        outputs.setLandscapes(countLandscapes)
        outerIterations = 0
        fitnessDistribution = []
        attemptedFlipsDist = []
        acceptedFlipsDist = []
        while outerIterations < countLandscapes:
            self.logger.info("Begin Searching Landscape #: " + str(outerIterations))
            self.setup()
            self.refreshFitnessContributions(self.__nodeConfig)
            systemFitness = self.getFitness(self.__nodeConfig)
            self.logState(self.__nodeConfig, systemFitness)
            while 1:
                prevNodeConfig = list(self.__nodeConfig)
                [mutatedConfig, mutatedFitness] = self.searchNext(self.__nodeConfig,
                                                    systemFitness, transWriter,
                                                    keyVal, countLandscapes,
                                                    outerIterations)
                self.logState(mutatedConfig, mutatedFitness)
                if (mutatedConfig == prevNodeConfig):
                    break
                self.__nodeConfig = list(mutatedConfig)
                systemFitness = mutatedFitness
            fitnessDistribution.append(systemFitness)
            attemptedFlipsDist.append(self.__attemptedFlips)
            acceptedFlipsDist.append(self.__acceptedFlips)
            self.logger.info("End Searching Landscape #: " + str(outerIterations))
            outerIterations += 1
        outputs.setFinessDistribution(fitnessDistribution)
        outputs.setAttemptedFlipsDistribution(attemptedFlipsDist)
        outputs.setAcceptedFlipsDistribution(acceptedFlipsDist)
        transactionCSVFile.close()
        return outputs

""" End of Class NK """
