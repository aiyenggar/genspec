# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:50:00 2015

@author: aiyenggar
The sim class encapsulates the inputs and outputs of a simulation
"""

from enum import Enum
import random
import numpy

def getRandom():
    """ Return an Random Number between 0 and 1 """
    return random.random()

def getRandomInt(start, end):
    return random.randint(start, end)

class KDistribution(Enum):
    FIXED = 1
    NORMAL = 2

class SearchMethod(Enum):
    GREEDY = 1 # TODO: Change to the formal term
    STEEPEST = 2 # TODO: Change to the formal term

A_DEFAULT = 2

class SimInput:
    def __init__(self, n, k, a=A_DEFAULT):
        # Check that n is positive, k is positive and less than n
        self.__nVal = n
        self.__kVal = k
        self.__aVal = a
        self.__kSystem = KDistribution.FIXED
        self.__adjMatrix = None
        self.__searchMethod = SearchMethod.STEEPEST

    def __del__(self):
        pass

    def setKSystem(self, kSys):
        self.__kSystem = kSys

    def setSearchMethod(self, method):
        self.__searchMethod = method

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
        return None

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

LANDSCAPES_DEFAULT = 100

class SimOutput:
    def __init__(self):
        self.__landscapes = LANDSCAPES_DEFAULT
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