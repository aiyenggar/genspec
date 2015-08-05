# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:47:51 2015

@author: aiyenggar
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())