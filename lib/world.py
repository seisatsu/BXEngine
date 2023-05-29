##################
# BXEngine       #
# world.py       #
# Copyright 2021 #
# Sei Satzparad  #
##################

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

from random import randint

import pygame

from lib.logger import Logger
from lib.room import Room


class World(object):
    """
    A class to represent the game world.
    """

    def __init__(self, config, app, resource):
        self.config = config
        self.app = app
        self.dir = self.config["world"]
        self.vars = None
        self.room = None
        self.resource = resource
        self.log = Logger("World")
        self.funvalue = None

    def load(self) -> bool:
        """
        Load the world descriptor JSON file.
        """
        self.vars = self.resource.load_json("world.json", "world")

        # Check if we successfully loaded the file.
        if not self.vars:
            self.log.critical("load(): Unable to load game world: {0}".format(self.config["world"]))
            return False
        self.log.info("load(): Finished loading game world: {0} ({1})".format(self.config["world"], self.vars["name"]))

        # Set our window title to the world name.
        pygame.display.set_caption(self.vars["name"])

        # Configure the funvalue.
        if "funvalue" not in self.app.database:
            self.app.database["funvalue"] = randint(self.vars["funvalue_range"][0], self.vars["funvalue_range"][1])
        self.funvalue = self.app.database["funvalue"]

        # Done.
        return self.change_room(self.vars["first_room"])

    def navigate(self, direction: str) -> bool:
        """
        Change rooms by exit name in the current room.
        """
        if direction in self.room.vars["exits"]:
            return self.change_room(self.room.vars["exits"][direction])
        self.log.warn("navigate(): Attempt to navigate through non-existent exit: {0}".format(direction))
        return False

    def change_room(self, room_file: str) -> bool:
        """
        Change rooms by room descriptor filename.
        """
        # If there is a colon in the room name, a particular view is being chosen.
        # Otherwise, load the "default" view.
        if ":" in room_file:
            room_file, view_name = room_file.split(":")
        else:
            view_name = "default"

        # Create a Room class instance for this room and view. Load the data.
        self.room = Room(self.config, self.app, self, self.resource, room_file, view_name)
        self.room._load()

        # Make sure we loaded correctly.
        if not self.room.vars:
            self.log.error("change_room(): Unable to load room and view: {0}:{1}".format(room_file, view_name))
            return False

        # Perform overlay cleanup if necessary.
        if hasattr(self.app, "overlay"):
            self.app.overlay._cleanup()

        # Done.
        return True
