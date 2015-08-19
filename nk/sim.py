# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:50:00 2015

@author: aiyenggar
The sim class encapsulates the inputs and outputs of a simulation
"""
import logging
from enum import Enum
import random
import numpy
import settings

def getRandom():
    """ Return an Random Number between 0 and 1 """
    return random.random()

def getRandomInt(start, end, avoid={}):
    """ Generate a random number in [start, end] that is not in avoid """
    """ The below assert is not an accurate test. It will fail when avoid includes entries outside start - end """
    assert (end-start+1 > len(avoid)), "Avoid includes all possibilities. Unable to generate random"
    rand = random.randint(start, end)
    while rand in avoid: #We found a random that the user does not want
        rand = random.randint(start, end)
    return rand

class KDistribution(Enum):
    FIXED = 1
    NORMAL = 2

class SearchMethod(Enum):
    GREEDY = 1
    STEEPEST = 2
    RANDOMTHENSTEEPEST = 3

class SimInput:
    def __init__(self, n, k, a=settings.A_DEFAULT):
        # Check that n is positive, k is positive and less than n
        self.__nVal = n
        self.__kVal = k
        self.__aVal = a
        self.__kSystem = KDistribution.FIXED
        self.__adjMatrix = None
        self.__searchMethod = SearchMethod.GREEDY
        self.__mutateDistance = 1
        self.__precision = settings.CONTRIBUTION_PRECISION
        self.__cumulativeDistance = True
        self.logger =  logging.getLogger(__name__)

    def __del__(self):
        pass

    def setKSystem(self, kSys):
        self.__kSystem = kSys

    def setSearchMethod(self, method):
        self.__searchMethod = method

    def setMutateDistance(self, distance):
        if distance >= 1:
            self.__mutateDistance = distance
        else:
            self.logger.error("Invalid distance parameter to setMutateDistance: " + str(distance))

    def setCumulativeDistance(self, boolVal):
        self.__cumulativeDistance = boolVal
    
    def cumulativeDistance(self):
        return self.__cumulativeDistance

    def nValue(self):
        return self.__nVal

    def kValue(self):
        return self.__kVal

    def aValue(self):
        return self.__aVal

    def adjMatrix(self):
        return self.__adjMatrix

    def searchMethod(self):
        return self.__searchMethod

    def searchMethodString(self):
        if self.__searchMethod == SearchMethod.STEEPEST:
            return "STEEPEST"
        if self.__searchMethod == SearchMethod.GREEDY:
            return "GREEDY"
        if self.__searchMethod == SearchMethod.RANDOMTHENSTEEPEST:
            return "RandomThenSteepest"
        return None

    def mutateDistance(self):
        return self.__mutateDistance

    def precision(self):
        return self.__precision

    def generateAdjMatrix(self, kSys=None):
        if (self.__nVal <= self.__kVal):
            return None

        if (kSys == None):
            kSys = self.__kSystem
        else:
            #Perform a check to ensure kSys is valid
            self.__kSystem = kSys

        if (self.__kSystem == KDistribution.FIXED):
            self.__adjMatrix = list([])
            for nodeIndex in range(0, self.__nVal):
                row = list([])
                # Initialize all entries with 0 (No Correlation)
                for rowIndex in range(0, self.__nVal):
                    row.append(0)
                # A node depends on itself so set that to 1
                row[nodeIndex] = 1
                # Find __kVal other nodes at random to set to 1
                numAdjacent = self.__kVal
                while numAdjacent > 0:
                    testIndex = getRandomInt(0, -1 + self.__nVal)
                    if (row[testIndex] == 0):
                        row[testIndex] = 1
                        # Decrement numAdjacent only if you found one
                        numAdjacent -= 1
                self.__adjMatrix.append(row)
        elif (self.__kSystem == KDistribution.NORMAL):
            None
        else:
            None

class SimOutput:
    def __init__(self):
        self.__landscapes = settings.LANDSCAPES_DEFAULT
        self.__fitnessDistribution = None
        self.__attemptedFlips = None
        self.__acceptedFlips = None
    def __del__(self):
        pass

    def setLandscapes(self, lScapes):
        self.__landscapes = lScapes

    def setFinessDistribution(self, distribution):
        self.__fitnessDistribution = distribution

    def setAttemptedFlipsDistribution(self, distribution):
        self.__attemptedFlips = distribution

    def setAcceptedFlipsDistribution(self, distribution):
        self.__acceptedFlips = distribution

    def landscapes(self):
        return self.__landscapes

    def meanFitness(self):
        return numpy.mean(self.__fitnessDistribution)

    def stddevFitness(self):
        return numpy.std(self.__fitnessDistribution)

    def meanAttemptedFlips(self):
        return numpy.mean(self.__attemptedFlips)

    def stddevAttemptedFlips(self):
        return numpy.std(self.__attemptedFlips)

    def meanAcceptedFlips(self):
        return numpy.mean(self.__acceptedFlips)

    def stddevAcceptedFlips(self):
        return numpy.std(self.__acceptedFlips)

    def lenFitnessDistribution(self):
        return len(self.__fitnessDistribution)

    def lenAttemptedFlips(self):
        return len(self.__attemptedFlips)

    def lenAcceptedFlips(self):
        return len(self.__acceptedFlips)
        
class SimAttemptStatistics:
    def __init__(self, keyVal, nVal, kVal, aVal):
        self.key = keyVal
        self.nValue = nVal
        self.kValue = kVal
        self.aValue = aVal
        self.searchMethod = SearchMethod.GREEDY
        self.distance = 0
        self.isDistanceCumulative = True
        self.landscape = 0
        self.numLandscapes = 0
        self.numAttemptedFlips = 0
        self.numAcceptedFlips = 0
        self.wasFlipAccepted = 0
        self.currentConfig = ""
        self.currentFitness = []
        self.consideredConfig = ""
        self.consideredContributions = []
        self.consideredFitness = []        
        
    def __del__(self):
        pass
    