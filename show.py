#!/usr/bin/python3

import datetime as dt
import os
import sys
import time

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "waveshare_epd")
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd5in83bc
from draw import Drawer, IMAGE_SIZE
from PIL import Image, ImageDraw, ImageFont

# import traceback

logging.basicConfig(level=logging.INFO)


def show_image(epd, image):
    """
    Renders an image to the display. Handles splitting colours.
    """
    image = image.convert("RGB")
    # Create red & black images of the right size
    black_image = Image.new("1", IMAGE_SIZE, 1)
    red_image = Image.new("1", IMAGE_SIZE, 1)
    # Copy pixels into them
    for x in range(IMAGE_SIZE[0]):
        for y in range(IMAGE_SIZE[1]):
            pixel = image.getpixel((x, y))
            if pixel[1] < 100:
                if pixel[0] > 125:
                    red_image.putpixel((x, y), 0)
                else:
                    black_image.putpixel((x, y), 0)
    epd.init()
    try:
        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        time.sleep(2)
    finally:
        epd.sleep()


logging.info("Display initialising")
epd = epd5in83bc.EPD()
epd.init()
epd.Clear()
logging.info("Drawer initialising")
drawer = Drawer()
cleared = False
try:
    while True:
        now = dt.datetime.now()
        hour = now.hour
        if hour < 1 or hour > 4:
            logging.info("Rendering")
            img = drawer.render()
            logging.info("Drawing to display")
            show_image(epd, img)
            if cleared:
                logging.info("Good morning " + now.strftime("%Y-%m-%d %H:%M:%S"))
            cleared = False
            logging.info("Sleeping")
        elif not cleared:
            epd.init()
            epd.Clear()
            epd.sleep()
            logging.info("Good night " + now.strftime("%Y-%m-%d %H:%M:%S"))
            cleared = True
        time.sleep(900)

except IOError as e:
    logging.info("exception")
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd5in83bc.epdconfig.module_exit()
    exit()

finally:
    epd.sleep()
