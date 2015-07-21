# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 14:36:21 2015

@author: aiyenggar
"""
import random
import numpy

A_GLOBAL = 2

def getAdjacencyMatrix(nVal, kVal):
    matrix = list([])
    for nodeIndex in range(0, nVal):
        row = list([])
        for rowIndex in range(0, nVal):
            row.append(0)
        row[nodeIndex] = 1
        numAdjacent = kVal
        while numAdjacent > 0:
            testIndex = getRandomInt(0, nVal-1)
            if (row[testIndex] == 0):
                row[testIndex] = 1
                numAdjacent -= 1
        matrix.append(row)
    return matrix
        
        
def getRandom():
    return random.random()

def getRandomInt(start, end):
    return random.randint(start, end)
    
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
        conMap[hashKey] = getRandom()
    retContribution = conMap.get(hashKey)
    return [retContribution, conMap]
        
def initAllNodes(nVal, kVal, aVal):
    configuration = list([])
    nodeMap = dict({})
    for index in range(0, nVal):
        configuration.append(getRandomInt(0,aVal-1))
        nodeMap[index] = dict({})
    return [configuration, nodeMap]
    
def getFitness(nVal, kMap, aVal, configuration, aMap):
    sumWeights = 0.0
    for index in range(0, nVal):
        [contrib, fitContrib] = getContribution(index, configuration, kMap, aMap[index], aVal)
        sumWeights += contrib
    return sumWeights/nVal
    
def getMutatedValue(currentValue, numValues):
    newValue = getRandomInt(0, numValues - 1)
    while (newValue == currentValue):
        newValue = getRandomInt(0, numValues - 1)
    return newValue

def mutateConfig(numNodes, configuration, numValues):
    newConf = list(configuration)
    indexToMutate = getRandomInt(0, numNodes - 1)
    newConf[indexToMutate] = getMutatedValue(newConf[indexToMutate], numValues)
    return [indexToMutate, newConf]

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
    return [selectedConfig, selectedFitness, fitContribution]
    
def dumpFitnessMap(nodeIndex, iMap): 
    for entry in iMap.keys():
        print("Fitness Map " + str(nodeIndex) + " = " + str(entry) + " : " + str(iMap[entry]))

def dumpAllFitnessMaps(aMap):
        for j in aMap.keys():
            dumpFitnessMap(j, aMap[j])

        
def updateFitnessContributions(nVal, kVal, kMap, aVal, configuration, fitContribution):
    nextNode = 0
    while nextNode < nVal:
        maxConfig = aVal ** (kVal + 1)
        if len(fitContribution[nextNode]) < maxConfig:
            [nextContribution, fitContribution[nextNode]] = getContribution(nextNode, configuration, kMap, fitContribution[nextNode], aVal)
        nextNode += 1
    return fitContribution

def simulateNK(nVal, kVal, aVal, iterations):
    print("Simulating N:" + str(nVal) + " K:" + str(kVal))
    outerIterations = 0
    landscapeDist = []
    while outerIterations < iterations: 
        [nodeConfig, fitnessMap] = initAllNodes(nVal, kVal, aVal)
        adjList = getAdjacencyMatrix(nVal, kVal)
        fitnessMap = updateFitnessContributions(nVal, kVal, adjList, aVal, nodeConfig, fitnessMap)      
        systemFitness = getFitness(nVal, adjList, aVal, nodeConfig, fitnessMap)
        while 1:
            [mutatedNodeConfig, mutatedFitness, fitnessMap] = mutateConfigIncremental(nVal, kVal, adjList, aVal, nodeConfig, fitnessMap, systemFitness)
            if (mutatedNodeConfig == nodeConfig):
                break
            nodeConfig = mutatedNodeConfig
            systemFitness = mutatedFitness    
        outerIterations += 1
        landscapeDist.append(systemFitness)
    mu = numpy.mean(landscapeDist)
    sd = numpy.std(landscapeDist)
    return [mu,sd]

a = A_GLOBAL
#nList = [8, 16, 24, 48, 96]
kList = [0, 2, 4, 8, 16, 24, 48, 96]
nList = [8, 16, 24]
#kList = [2]
for nVal in nList:
    for kVal in kList:
        if kVal <= nVal:
            if kVal == nVal:
                [nmu, nsd] = simulateNK(nVal, kVal-1, a, 100)
            else:
                [nmu, nsd] = simulateNK(nVal, kVal, a, 100)
            print("N = " + str(nVal) + " K = " + str(kVal) + " Mean :" + str(nmu) + " SD: " + str(nsd))