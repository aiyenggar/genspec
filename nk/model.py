# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:37:01 2015

@author: aiyenggar
"""
from nk import sim

class model:
    def __init__(self, simObj):
        self.__simObject = simObj
        self.__nodeConfig = None
        self.__fitnessDict = None

    
    def setup(self):
        self.__nodeConfig = list([])
        self.__fitnessDict = dict({})
        for index in range(0, self.__simObject.nValue()):
            self.__nodeConfig.append(sim.getRandomInt(0,self.__simObject.aValue()-1))
            self.__fitnessDict[index] = dict({})

    def updateNodeContribution(self, nodeIndex, configuration):
        maskedConfig = list(configuration)
        hashKey = ()
        colValue = 0
        for kValue in self.__simObject.adjMatrix()[nodeIndex]:
            if kValue == 0:
                maskedConfig[colValue] = self.__simObject.aValue()
            colValue += 1
        hashKey = tuple(maskedConfig)
        if hashKey not in self.__fitnessDict[nodeIndex]:
            self.__fitnessDict[nodeIndex][hashKey] = sim.getRandom()
        return self.__fitnessDict[nodeIndex][hashKey]
        
    def refreshFitnessContributions(self, configuration):
        maxConfig = self.__simObject.aValue() ** (self.__simObject.kValue() + 1)
        nextNode = 0
        while nextNode < self.__simObject.nValue():
            if len(self.__fitnessDict[nextNode]) < maxConfig:
                self.updateNodeContribution(nextNode, configuration)
            nextNode += 1

    def getFitness(self, configuration):
        sumWeights = 0.0
        for index in range(0, self.__simObject.nValue()):
            sumWeights += self.updateNodeContribution(index, configuration)
        return sumWeights/self.__simObject.nValue()
        
    """ Get node configurations that are 1 hamming distance from given node """
    def getNeighbours(self, configuration):
        listNeighbours = []
        nextNode = 0
        while (nextNode < self.__simObject.nValue()):  
            nextAllele = 0
            while (nextAllele < self.__simObject.aValue()):
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
        neighbours = self.getNeighbours(nodeConfig)
        for adjConfig in neighbours:           
            self.refreshFitnessContributions(adjConfig)
            systemFitness = self.getFitness(adjConfig)
            if (systemFitness > selectedFitness):
                selectedConfig = list(adjConfig)
                selectedFitness = systemFitness
        return [selectedConfig, selectedFitness]


    def runSimulation(self):
        cur = self.__simObject
#        print("Simulating N:" + str(cur.nValue()) + " K:" + str(cur.kValue()))
        outerIterations = 0
        landscapeDist = []
        while outerIterations < cur.landscapes(): 
            self.setup()
            self.refreshFitnessContributions(self.__nodeConfig)
            systemFitness = self.getFitness(self.__nodeConfig)
            while 1:
                prevNodeConfig = list(self.__nodeConfig)
                [mutatedNodeConfig, mutatedFitness] = self.mutate(self.__nodeConfig, systemFitness)
                if (mutatedNodeConfig == prevNodeConfig):
                    break
                self.__nodeConfig = list(mutatedNodeConfig)
                systemFitness = mutatedFitness    
            outerIterations += 1
            landscapeDist.append(systemFitness)
        return landscapeDist