# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""

from nk import sim, model
#kList = [0, 2, 4, 8, 16, 24, 48, 96]
kList = [0, 2, 4, 8, 16, 24]
#nList = [8, 16, 24, 48, 96]
nList = [8, 16, 24]
landscapes = 100
results = []
for nVal in nList:
    for kVal in kList:
        if kVal <= nVal:
            if kVal == nVal:
                input = sim.SimInput(nVal, kVal-1)
            else:
                input = sim.SimInput(nVal, kVal)
            input.generateAdjMatrix()
            simulation = model.NK(input)
            output = simulation.runSimulation(landscapes)
            print("N=" + str(input.nValue()) + 
                    " K=" + str(input.kValue()) + " " +
                    str(round(output.meanFitness(),2)) + 
                    " (" + str(round(output.stddevFitness(), 2)) + ")" +
                    " " + str(round(output.meanAttemptedFlips(),2)) + 
                    " " + str(round(output.meanAcceptedFlips(),2))
                 )
            results.append([input, output])
            input = None
            simulation = None
            output = None