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

import json
import os
import sys

import pygame
import pygame_gui

from lib.app import App
from lib.world import World
from lib.util import resource_path

CAPTION = "Backrooms Alpha"


def load_config():
    """
    Load the JSON config file.
    """
    with open("config.json") as f:
        config = json.load(f)
    return config


def load_images(config):
    """
    We load the common images here that are needed by the rest of the engine.
    This includes navigation and action indicators.
    """
    images = {"chevron_left": pygame.transform.scale(pygame.image.load(resource_path("images/chevron_left.png")),
                                                     config["navigation"]["indicator_size"]),
              "chevron_right": pygame.transform.scale(pygame.image.load(resource_path("images/chevron_right.png")),
                                                      config["navigation"]["indicator_size"]),
              "chevron_up": pygame.transform.scale(pygame.image.load(resource_path("images/chevron_up.png")),
                                                   config["navigation"]["indicator_size"]),
              "chevron_down": pygame.transform.scale(pygame.image.load(resource_path("images/chevron_down.png")),
                                                     config["navigation"]["indicator_size"]),
              "arrow_forward": pygame.transform.scale(pygame.image.load(resource_path("images/arrow_forward.png")),
                                                      config["navigation"]["indicator_size"]),
              "arrow_backward": pygame.transform.scale(pygame.image.load(resource_path("images/arrow_backward.png")),
                                                       config["navigation"]["indicator_size"]),
              "arrow_double": pygame.transform.scale(pygame.image.load(resource_path("images/arrow_double.png")),
                                                     config["navigation"]["indicator_size"]),
              "look": pygame.transform.scale(pygame.image.load(resource_path("images/look.png")),
                                             config["navigation"]["indicator_size"]),
              "use": pygame.transform.scale(pygame.image.load(resource_path("images/use.png")),
                                            config["navigation"]["indicator_size"]),
              "lookuse": pygame.transform.scale(pygame.image.load(resource_path("images/lookuse.png")),
                                                config["navigation"]["indicator_size"]),
              "go": pygame.transform.scale(pygame.image.load(resource_path("images/go.png")),
                                           config["navigation"]["indicator_size"]),
              "lookgo": pygame.transform.scale(pygame.image.load(resource_path("images/lookgo.png")),
                                               config["navigation"]["indicator_size"])}
    return images


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    config = load_config()
    images = load_images(config)

    pygame.display.set_caption(CAPTION)
    pygame.display.set_mode(config["window"]["size"])
    gui = pygame_gui.UIManager(config["window"]["size"])

    world = World(config)
    world.load()
    App(config, images, world, gui).main_loop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
