# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""

from nk import sim, model
#kList = [0, 2, 4, 8, 16, 24, 48, 96]
kList = [0, 2, 4, 8]
nList = [8, 16, 24, 48]
expResults = []
for nVal in nList:
    for kVal in kList:
        if kVal <= nVal:
            if kVal == nVal:
                test = sim.sim(nVal, kVal-1)
            else:
                test = sim.sim(nVal, kVal)

        test.generateAdjMatrix()
        myModel = model.model(test)
        distri = myModel.runSimulation()
        test.setFinessDistribution(distri)
        print("N = " + str(test.nValue()) + " K = " + str(test.kValue()) + 
                " Mean = " + str(round(test.meanFitness(),2)) + 
                " SD = " + str(round(test.stddevFitness(), 2)))
        expResults.append(test)
        test = None
        myModel = None