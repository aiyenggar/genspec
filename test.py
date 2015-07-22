# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""

from nk import sim, model

test = sim.sim(8, 0)
test.generateAdjMatrix()
myModel = model.model(test)
test.setFinessDistribution(myModel.runSimulation())
mean = round(test.meanFitness(),2)
sd = round(test.stddevFitness(), 2)
print("N = " + str(test.nValue()) + " K = " + str(test.kValue()) + " Mean = " + str(mean) + " SD = " + str(sd))
