# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:37:01 2015

@author: aiyenggar
"""
from nk import sim

def initAllNodes(nVal, kVal, aVal):
    configuration = list([])
    nodeMap = dict({})
    for index in range(0, nVal):
        configuration.append(sim.getRandomInt(0,aVal-1))
        nodeMap[index] = dict({})
    return [configuration, nodeMap]
    
def updateFitnessContributions(nVal, kVal, kMap, aVal, configuration, fitContribution):
    nextNode = 0
    while nextNode < nVal:
        maxConfig = aVal ** (kVal + 1)
        if len(fitContribution[nextNode]) < maxConfig:
            [nextContribution, fitContribution[nextNode]] = getContribution(nextNode, configuration, kMap, fitContribution[nextNode], aVal)
        nextNode += 1
    return fitContribution

    
def mutateConfigIncremental(nVal, kVal, kMap, aVal, nodeConfig, fitContribution, nodeFitness):
    selectedConfig = nodeConfig
    selectedFitness = nodeFitness
    neighbours = getNeighbours(nVal, nodeConfig, aVal)
    for adjConfig in neighbours:  
        fitContribution = updateFitnessContributions(nVal, kVal, kMap, aVal, adjConfig, fitContribution)
        systemFitness = getFitness(nVal, kMap, aVal, adjConfig, fitContribution)
        if (systemFitness > selectedFitness):
            selectedConfig = list(adjConfig)
            selectedFitness = systemFitness
    return [selectedConfig, selectedFitness]


""" Get node configurations that are 1 hamming distance from given node """
def getNeighbours(numNodes, configuration, numValues):
    listNeighbours = []
    nextNode = 0
    while (nextNode < numNodes):  
        nextAllele = 0
        while (nextAllele < numValues):
            if (nextAllele != configuration[nextNode]):
                nextNeighbour = list(configuration)
                nextNeighbour[nextNode] = nextAllele
                listNeighbours.append(nextNeighbour)
            nextAllele += 1
        nextNode += 1
    return listNeighbours

def getFitness(nVal, kMap, aVal, configuration, aMap):
    sumWeights = 0.0
    for index in range(0, nVal):
        [contrib, fitContrib] = getContribution(index, configuration, kMap, aMap[index], aVal)
        sumWeights += contrib
    return sumWeights/nVal

def getContribution(nodeIndex, configuration, kMap, conMap, aVal):
    maskedConfig = list(configuration)
    hashKey = ()
    colValue = 0
    for kValue in kMap[nodeIndex]:
        if kValue == 0:
            maskedConfig[colValue] = aVal
        colValue += 1
    hashKey = tuple(maskedConfig)
    if hashKey not in conMap:
        conMap[hashKey] = sim.getRandom()
    retContribution = conMap.get(hashKey)
    return [retContribution, conMap]
    

class model:
    def __init__(self, simObj):
        self.__simObject = simObj
        self.__nodeConfig = None
        self.__fitnessDict = None
        
    def runSimulation(self):
        cur = self.__simObject
#        print("Simulating N:" + str(cur.nValue()) + " K:" + str(cur.kValue()))
        outerIterations = 0
        landscapeDist = []
        while outerIterations < cur.landscapes(): 
            [self.__nodeConfig, self.__fitnessDict] = initAllNodes(
                                                        cur.nValue(), 
                                                        cur.kValue(), 
                                                        cur.aValue()
                                                        )
           
            self.__fitnessDict = updateFitnessContributions(cur.nValue(),
                                                            cur.kValue(),
                                                            cur.adjMatrix(),
                                                            cur.aValue(),
                                                            self.__nodeConfig,
                                                            self.__fitnessDict
                                                            )
            systemFitness = getFitness(cur.nValue(), cur.adjMatrix(),
                                       cur.aValue(),self.__nodeConfig,
                                       self.__fitnessDict
                                       )
            while 1:
                prevNodeConfig = list(self.__nodeConfig)
                [mutatedNodeConfig, mutatedFitness] = mutateConfigIncremental(cur.nValue(),
                                                                            cur.kValue(),
                                                                            cur.adjMatrix(),
                                                                            cur.aValue(),
                                                                            self.__nodeConfig,
                                                                            self.__fitnessDict,
                                                                            systemFitness
                                                                            )
                if (mutatedNodeConfig == prevNodeConfig):
                    break
                self.__nodeConfig = list(mutatedNodeConfig)
                systemFitness = mutatedFitness    
            outerIterations += 1
            landscapeDist.append(systemFitness)
        return landscapeDist