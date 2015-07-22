# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:37:01 2015

@author: aiyenggar
"""
from nk import sim

class NK:
    def __init__(self, simInput):
        self.__inputs = simInput
        self.__nodeConfig = None
        self.__fitnessDict = None
    
    def setup(self):
        self.__nodeConfig = list([])
        self.__fitnessDict = dict({})
        self.__attemptedFlips = 0
        self.__acceptedFlips = 0
        for index in range(0, self.__inputs.nValue()):
            nextNodeValue = sim.getRandomInt(0,self.__inputs.aValue()-1)
            self.__nodeConfig.append(nextNodeValue)
            self.__fitnessDict[index] = dict({})

    def updateNodeContribution(self, nodeIndex, configuration):
        maskedConfig = list(configuration)
        hashKey = ()
        colValue = 0
        for kValue in self.__inputs.adjMatrix()[nodeIndex]:
            if kValue == 0:
                maskedConfig[colValue] = self.__inputs.aValue()
            colValue += 1
        hashKey = tuple(maskedConfig)
        if hashKey not in self.__fitnessDict[nodeIndex]:
            self.__fitnessDict[nodeIndex][hashKey] = sim.getRandom()
        return self.__fitnessDict[nodeIndex][hashKey]
        
    def refreshFitnessContributions(self, configuration):
        maxConfig = self.__inputs.aValue() ** (self.__inputs.kValue() + 1)
        nextNode = 0
        while nextNode < self.__inputs.nValue():
            if len(self.__fitnessDict[nextNode]) < maxConfig:
                self.updateNodeContribution(nextNode, configuration)
            nextNode += 1

    def getFitness(self, configuration):
        runningFitnessSum = 0.0
        for index in range(0, self.__inputs.nValue()):
            runningFitnessSum += self.updateNodeContribution(index, configuration)
        return runningFitnessSum/self.__inputs.nValue()
        
    """ Get node configurations that are 1 hamming distance from given node """
    def getNeighbours(self, configuration):
        listNeighbours = []
        nextNode = 0
        while (nextNode < self.__inputs.nValue()):  
            nextAllele = 0
            while (nextAllele < self.__inputs.aValue()):
                if (nextAllele != configuration[nextNode]):
                    nextNeighbour = list(configuration)
                    nextNeighbour[nextNode] = nextAllele
                    listNeighbours.append(nextNeighbour)
                nextAllele += 1
            nextNode += 1
        return listNeighbours
    
    def mutate(self, nodeConfig, nodeFitness):
        selectedConfig = nodeConfig
        selectedFitness = nodeFitness
        if (self.__inputs.searchMethod() == sim.SearchMethod.STEEPEST_NEIGHBOUR):
            neighbours = self.getNeighbours(nodeConfig)
            for adjConfig in neighbours:
                self.__attemptedFlips += 1
                self.refreshFitnessContributions(adjConfig)
                systemFitness = self.getFitness(adjConfig)
                if (systemFitness > selectedFitness):
                    self.__acceptedFlips += 1
                    selectedConfig = list(adjConfig)
                    selectedFitness = systemFitness
            return [selectedConfig, selectedFitness]
        elif (self.__inputs.searchMethod() == sim.SearchMethod.GREEDY):
            exploredNeighbours = {}
            maxNeighbours = self.__inputs.nValue() * (self.__inputs.aValue()-1)
            while len(exploredNeighbours) < maxNeighbours:
                randomNode = sim.getRandomInt(0, self.__inputs.nValue()-1)
                randomAllele = sim.getRandomInt(0, self.__inputs.aValue()-1)
                # Find an Allele at position randomNode that is different
                while randomAllele == nodeConfig[randomNode]:
                    randomAllele = sim.getRandomInt(0, self.__inputs.aValue()-1)
                randomConfig = list(nodeConfig)
                randomConfig[randomNode] = randomAllele
                self.__attemptedFlips += 1
                self.refreshFitnessContributions(randomConfig)
                systemFitness = self.getFitness(randomConfig)
                hashKey = tuple(randomConfig)
                if hashKey not in exploredNeighbours:
                    exploredNeighbours[hashKey] = 1
                else:
                    exploredNeighbours[hashKey] += 1                 
                if (systemFitness > selectedFitness):
                    self.__acceptedFlips += 1
                    selectedConfig = list(randomConfig)
                    selectedFitness = systemFitness
                    return [selectedConfig, selectedFitness]  
            return [selectedConfig, selectedFitness]
        else:
            return None


    def runSimulation(self, countLandscapes):
        outputs = sim.SimOutput()
        outputs.setLandscapes(countLandscapes)
        outerIterations = 0
        fitnessDistribution = []
        attemptedFlipsDist = []
        acceptedFlipsDist = []
        while outerIterations < countLandscapes: 
            self.setup()
            self.refreshFitnessContributions(self.__nodeConfig)
            systemFitness = self.getFitness(self.__nodeConfig)
            while 1:
                prevNodeConfig = list(self.__nodeConfig)
                [mutatedConfig, mutatedFitness] = self.mutate(
                                                    self.__nodeConfig, 
                                                    systemFitness
                                                    )
                if (mutatedConfig == prevNodeConfig):
                    break
                self.__nodeConfig = list(mutatedConfig)
                systemFitness = mutatedFitness    
            outerIterations += 1
            fitnessDistribution.append(systemFitness)
            attemptedFlipsDist.append(self.__attemptedFlips)
            acceptedFlipsDist.append(self.__acceptedFlips)
        outputs.setFinessDistribution(fitnessDistribution)
        outputs.setAttemptedFlipsDistribution(attemptedFlipsDist)
        outputs.setAcceptedFlipsDistribution(acceptedFlipsDist)
        return outputs
        
""" End of Class NK """
