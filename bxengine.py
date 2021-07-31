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
import pygame_gui

from lib.app import App
from lib.logger import Logger, timestamp
from lib.resourcemanager import ResourceManager
from lib.world import World

VERSION = "BXEngine PreAlpha"


def load_images(config, resource):
    """
    We load the common images here that are needed by the rest of the engine.
    This includes navigation and action indicators.
    """
    images = {
        "chevron_left": resource.load_image("images/chevron_left.png", config["navigation"]["indicator_size"]),
        "chevron_right": resource.load_image("images/chevron_right.png", config["navigation"]["indicator_size"]),
        "chevron_up": resource.load_image("images/chevron_up.png", config["navigation"]["indicator_size"]),
        "chevron_down": resource.load_image("images/chevron_down.png", config["navigation"]["indicator_size"]),
        "arrow_forward": resource.load_image("images/arrow_forward.png", config["navigation"]["indicator_size"]),
        "arrow_backward": resource.load_image("images/arrow_backward.png", config["navigation"]["indicator_size"]),
        "arrow_double": resource.load_image("images/arrow_double.png", config["navigation"]["indicator_size"]),
        "look": resource.load_image("images/look.png", config["navigation"]["indicator_size"]),
        "use": resource.load_image("images/use.png", config["navigation"]["indicator_size"]),
        "lookuse": resource.load_image("images/lookuse.png", config["navigation"]["indicator_size"]),
        "go": resource.load_image("images/go.png", config["navigation"]["indicator_size"]),
        "lookgo": resource.load_image("images/lookgo.png", config["navigation"]["indicator_size"])
    }
    return images


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    print("Welcome to {0}.".format(VERSION))
    print("Starting up...")

    resource = ResourceManager()

    print("Loading configuration...")
    config = resource._load_initial_config("config.json")
    log = Logger("BXEngine")

    log.info("Loading required images...")
    images = load_images(config, resource)
    if None in images.values():
        log.critical("Unable to load required images.")
        sys.exit(4)
    log.info("Finished loading required images.")

    pygame.display.set_caption(VERSION)
    pygame.display.set_mode(config["window"]["size"])
    gui = pygame_gui.UIManager(config["window"]["size"])

    log.info("Initializing game world...")
    world = World(config, resource)
    if not world.load():
        sys.exit(5)

    App(config, images, world, gui, resource)._main_loop()
    log.info("Shutting down...")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
