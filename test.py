# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 06:00:03 2015

@author: aiyenggar
"""
import os
import json
import logging.config

OUTPUT_LOG_LEVEL = 25
def setup_logging(
    default_path='logging.json',
    default_level=logging.ERROR,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

from nk import sim, model
setup_logging();
#kList = [0, 2, 4, 8, 16, 24, 48, 96]
kList = [0]
#nList = [8, 16, 24, 48, 96]
nList = [8]
landscapes = 100
results = []
logger =  logging.getLogger(__name__)
for nVal in nList:
    for kVal in kList:
        logger.debug("Starting Simulation: N = " + str(nVal) + " K = " + str(kVal))
        if kVal <= nVal:
            if kVal == nVal:
                input = sim.SimInput(nVal, kVal-1)
            else:
                input = sim.SimInput(nVal, kVal)
            input.generateAdjMatrix()
            simulation = model.NK(input)
            output = simulation.runSimulation(landscapes)
            logger.log(OUTPUT_LOG_LEVEL,
                    "N=" + str(input.nValue()) +
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
        else:
            logger.warning("K value is greater than N")
    logger.info("All K's Exhausted for N = " + str(nVal))