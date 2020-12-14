#!/bin/python3

import logging
import os
import sys

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "waveshare_epd")
if os.path.exists(libdir):
    sys.path.append(libdir)
import epd5in83bc

logging.basicConfig(level=logging.DEBUG)
epd = epd5in83bc.EPD()
logging.info("Clear...")
epd.init()
epd.Clear()

logging.info("Goto Sleep...")
epd.sleep()
epd.Dev_exit()
