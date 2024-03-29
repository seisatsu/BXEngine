#######################
# BXEngine            #
# world.py            #
# Copyright 2021-2023 #
# Sei Satzparad       #
#######################

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
from lib.roomview import Roomview


class World(object):
    """A class to represent the game world.

    :ivar config: This contains the engine's configuration variables.
    :ivar app: The main App instance.
    :ivar dir: The directory of the game world.
    :ivar vars: The JSON object representing the world file.
    :ivar roomview: The currently focused roomview.
    :ivar resource: The ResourceManager instance.
    :ivar log: The Logger instance for this class.
    :ivar funvalue: The world's funvalue, which is set on first load and affects what may happen this playthrough.
    """
    def __init__(self, config, app, resource):
        """World Class Initializer

        :param config: This contains the engine's configuration variables.
        :param app: The main App instance.
        :param resource: The ResourceManager instance.
        """
        self.config = config
        self.app = app
        self.dir = self.config["world"]
        self.vars = None
        self.roomview = None
        self.resource = resource
        self.log = Logger("World")
        self.funvalue = None

    def load(self) -> bool:
        """Load the world descriptor JSON file and prepare the world.

        :return: True if succeeded, False if failed.
        """
        self.vars = self.resource.load_json("world.json", "world")

        # Check if we successfully loaded the file.
        if not self.vars:
            self.log.critical("load(): Unable to load game world: {0}".format(self.config["world"]))
            return False
        self.log.info("load(): Finished loading game world: {0} ({1})".format(self.config["world"], self.vars["name"]))

        # Set our window title to the world name.
        self.set_caption()

        # Configure the funvalue. If none exists yet, it is chosen randomly just once, based on the range configured
        # in the world.json file. If a funvalue has already been chosen, load that out of the database.
        if "funvalue" not in self.app.database:
            self.app.database["funvalue"] = randint(self.vars["funvalue_range"][0], self.vars["funvalue_range"][1])
        self.funvalue = self.app.database["funvalue"]

        # Done.
        return self.change_roomview(self.vars["first_roomview"])

    def navigate(self, direction: str) -> bool:
        """Change roomviews by exit name in the current roomview.

        :param direction: Name of the direction to exit by.

        :return: True if succeeded, False if failed.
        """
        if direction in self.roomview.exits:
            return self.change_roomview(self.roomview.exits[direction])
        self.log.warn("navigate(): Attempt to navigate through non-existent exit: {0}".format(direction))
        return False

    def change_roomview(self, room_name: str) -> bool:
        """Change roomviews by room descriptor filename and optionally included view name.

        :param room_name: The room descriptor filename and optionally included view name.

        :return: True if succeeded, False if failed.
        """
        # If there is a colon in the room name, a particular view is being chosen.
        # Otherwise, load the "default" view.
        if ":" in room_name:
            room_name, view_name = room_name.split(":")
        else:
            view_name = "default"

        # Temporarily hold the previous roomview in case we need to switch back.
        backtrack = self.roomview

        # Create a Roomview class instance for this room and view. Load the data.
        self.roomview = Roomview(self.config, self.app, self, self.resource, room_name, view_name)
        self.roomview._load()

        # Make sure we loaded correctly.
        if not self.roomview.vars:
            self.log.error("change_roomview(): Unable to load room and view: {0}:{1}".format(room_name, view_name))
            self.roomview = backtrack
            return False

        # Perform overlay cleanup if necessary.
        if hasattr(self.app, "overlay"):
            self.app.overlay._cleanup()

        # Done.
        return True

    def set_caption(self, caption: [str, None] = None) -> bool:
        """Set the window title/caption.

        This is displayed in the window title area, after the world name.
        If "caption" is empty, just set the title to the world name by itself.

        :param: If given, the window caption to be set, otherwise reset the window title to just the world name.

        :return: True.
        """
        if caption:
            pygame.display.set_caption("{0} - {1}".format(self.vars["name"], caption))
        else:
            pygame.display.set_caption(self.vars["name"])
        return True

