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
from lib.databasemanager import DatabaseManager
from lib.logger import Logger
from lib.resourcemanager import ResourceManager

# This version string is printed when starting the engine.
VERSION = "BXEngine PreAlpha"


def load_images(config, resource, log):
    """
    We load the common images here that are needed by the rest of the engine.
    This includes navigation and action indicators.
    """
    # List of common images absolutely required before the engine will start.
    required_images = [
        "chevron_left",
        "chevron_right",
        "chevron_up",
        "chevron_down",
        "arrow_forward",
        "arrow_backward",
        "arrow_double",
        "look",
        "use",
        "lookuse",
        "go",
        "lookgo"
    ]

    # Load all images in the common/ folder into the loaded_images dict.
    loaded_images = {}  # Dict mapping image names to PyGame Surfaces for loaded images.
    common_directory_contents = os.listdir("common/")
    for common_file in common_directory_contents:
        split_ext = os.path.splitext(common_file)
        if split_ext[1] == ".png":
            loaded_images[split_ext[0]] = resource.load_image("common/{0}".format(common_file),
                                                              config["navigation"]["indicator_size"])

    # Make sure all of the required common images are present and loaded.
    # If not, give a warning and put a None in the loaded_images dict so we exit afterwards.
    # Any image that is present but fails to load is already given a None value by the resource manager.
    for image_name in required_images:
        if image_name not in loaded_images:
            log.error("Could not load required common image file: common/{0}.png".format(image_name))
            loaded_images[image_name] = None

    # Return the dict of loaded images.
    return loaded_images


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

    # Open the primary database.
    log.info("Opening primary database...")
    database = DatabaseManager(config)

    # Load all images from the common folder.
    log.info("Loading common images...")
    images = load_images(config, resource, log)
    if None in images.values():
        log.critical("Unable to load required common images.")
        sys.exit(7)
    log.info("Finished loading common images.")

    # Set the default window caption, set window size, and get the window surface.
    pygame.display.set_caption(VERSION)
    pygame.display.set_mode(config["window"]["size"])
    screen = pygame.display.get_surface()

    # Entry point to the main program.
    App(screen, config, images, resource, database)._main_loop()

    # Shut down.
    log.info("Shutting down...")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
