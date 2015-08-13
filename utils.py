# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:55:01 2015

@author: aiyenggar
"""
import logging.config
import os
import json
import time
import settings

def setupLogging(
    default_path='logging.json',
    default_level=logging.ERROR,
    env_key='LOG_CFG'):
    """
    Setup logging configuration

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

def logLine(logger):
    logger.info("---------------------------------------------")

def logInitialConditions(logger, inp, landscapes):
    logger.info(time.strftime("%Y-%m-%d %H:%M:%S") + " Simulating: N = " + str(inp.nValue()) + " K = " + str(inp.kValue()))
    logger.info("Search: " + inp.searchMethodString() + " Landscapes = " + str(landscapes))
    logger.info("Adjacency Matrix")
    adjMatrix = inp.adjMatrix()
    for row in adjMatrix:
        logger.info(row)
    logLine(logger)

def logResults(logger, inp, output, landscapes):
                logger.log(settings.OUTPUT_LOG_LEVEL,
                    "<N=" + str(inp.nValue()) +
                    " K=" + str(inp.kValue()) +
                    " Landscapes:" + str(landscapes) +
                    " Search:" + inp.searchMethodString() + "> " +
                    str(round(output.meanFitness(),2)) +
                    "(" + str(round(output.stddevFitness(), 2)) + ")" +
                    " " + str(round(output.meanAttemptedFlips(),2)) +
                    " " + str(round(output.meanAcceptedFlips(),2))
                 )