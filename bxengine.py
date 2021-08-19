#! /usr/bin/env python

#####################
# BXEngine          #
# bxengine.py       #
# Copyright 2021    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

"""
Started from example code written by Sean J. McKiernan 'Mekire'
* https://github.com/Mekire/pygame-samples/blob/master/drag_text.py
"""

import os
import sys

import pygame

from lib.app import App
from lib.logger import Logger
from lib.resourcemanager import ResourceManager

VERSION = "BXEngine PreAlpha"


def load_images(config, resource):
    """
    We load the common images here that are needed by the rest of the engine.
    This includes navigation and action indicators.
    """
    return {
        "chevron_left": resource.load_image("common/chevron_left.png", config["navigation"]["indicator_size"]),
        "chevron_right": resource.load_image("common/chevron_right.png", config["navigation"]["indicator_size"]),
        "chevron_up": resource.load_image("common/chevron_up.png", config["navigation"]["indicator_size"]),
        "chevron_down": resource.load_image("common/chevron_down.png", config["navigation"]["indicator_size"]),
        "arrow_forward": resource.load_image("common/arrow_forward.png", config["navigation"]["indicator_size"]),
        "arrow_backward": resource.load_image("common/arrow_backward.png", config["navigation"]["indicator_size"]),
        "arrow_double": resource.load_image("common/arrow_double.png", config["navigation"]["indicator_size"]),
        "look": resource.load_image("common/look.png", config["navigation"]["indicator_size"]),
        "use": resource.load_image("common/use.png", config["navigation"]["indicator_size"]),
        "lookuse": resource.load_image("common/lookuse.png", config["navigation"]["indicator_size"]),
        "go": resource.load_image("common/go.png", config["navigation"]["indicator_size"]),
        "lookgo": resource.load_image("common/lookgo.png", config["navigation"]["indicator_size"])
    }


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    # Set the window to be centered and initialize PyGame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    # Welcome message.
    print("Welcome to {0}.".format(VERSION))
    print("Starting up...")

    # We need to initialize ResourceManager first so we can load the config file.
    resource = ResourceManager()

    # Load the config file and initialize the logger.
    print("Loading configuration...")
    config = resource._load_initial_config("config.json")
    log = Logger("BXEngine")

    # Load the required images from the common folder.
    log.info("Loading required images...")
    images = load_images(config, resource)
    if None in images.values():
        log.critical("Unable to load required images.")
        sys.exit(4)
    log.info("Finished loading required images.")

    # Set the default window caption, set window size, and get the window surface.
    pygame.display.set_caption(VERSION)
    pygame.display.set_mode(config["window"]["size"])
    screen = pygame.display.get_surface()

    # Entry point to the main program.
    App(screen, config, images, resource)._main_loop()

    # Shut down.
    log.info("Shutting down...")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
