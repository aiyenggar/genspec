# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""
import logging
import utils
import settings
import time
from nk import sim, model

utils.setupLogging();

results = []
logger =  logging.getLogger(__name__)
landscapes = settings.landscapes
for nVal in settings.nList:
    for kVal in settings.kList:
        if kVal <= nVal:
            if kVal == nVal:
                params = sim.SimInput(nVal, kVal-1)
            else:
                params = sim.SimInput(nVal, kVal)

            params.setSearchMethod(sim.SearchMethod.GREEDY)
            params.setMutateDistance(2)
            params.generateAdjMatrix()

            utils.logInitialConditions(logger, params, landscapes)

            simulation = model.NK(params)
            key = int(round(time.time() * 1000))
            output = simulation.runSimulation(key, landscapes)

            utils.logResults(logger, params, output, landscapes)

            results.append([params, output])
            params = None
            simulation = None
            output = None
            utils.logLine(logger)
