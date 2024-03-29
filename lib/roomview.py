#######################
# BXEngine            #
# roomview.py         #
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

import random

from lib.logger import Logger


class Roomview(object):
    """A class to represent the current room and view.

    :ivar config: This contains the engine's configuration variables.
    :ivar app: The main App instance.
    :ivar world: The World instance.
    :ivar resource: The ResourceManager instance.
    :ivar file: The filename of the room.
    :ivar view: The name of the active view.
    :ivar vars: The JSON object representing the room file.
    :ivar image: The background image for this view.
    :ivar music: The music file loaded for this view, if any.
    :ivar exits: Dictionary of exit names to calculated destinations (for present exits only.)
    :ivar exits: Dictionary of "go" action rects to calculated destinations (for present exits only.)
    :ivar log: The Logger instance for this class.
    """

    def __init__(self, config, app, world, resource, room_file, view_name):
        """The Roomview initializer.

        :param config: This contains the engine's configuration variables.
        :param app: The main App instance.
        :param world: The World instance.
        :param resource: The ResourceManager instance.
        :param room_file: The filename of the room.
        :param view_name: The name of the active view.
        """
        self.config = config
        self.app = app
        self.world = world
        self.resource = resource
        self.file = room_file
        self.view = view_name
        self.title = None
        self.vars = None
        self.image = None
        self.music = None
        self.exits = {}
        self.action_exits = {}
        self.log = Logger("Roomview")

    def _load(self) -> bool:
        """Load the room descriptor JSON file. Also load the room image.

        :return: True if succeeded, False if failed.
        """
        # Attempt to load the room file.
        self.log.info("_load(): Loading room and view: {0}:{1}".format(self.file, self.view))
        whole_room = self.resource.load_json(self.file, "room")

        # We were unable to load the room file.
        if not whole_room:
            self.log.error("_load(): Unable to load room descriptor: {0}".format(self.file))
            return False

        # Make sure the view we are loading exists.
        if self.view not in whole_room:
            self.log.error("_load(): No such view in room: {0}: {1}".format(self.file, self.view))
            return False

        # Load the requested view.
        self.vars = whole_room[self.view]

        # Set the window caption to the roomview title, if one exists.
        if "title" in self.vars:
            self.title = self.vars["title"]
            self.world.set_caption(self.title)

        # Attempt to load the view's background image.
        self.image = self.resource.load_image(self.vars["image"], self.config["window"]["size"])

        # We were unable to load the background image.
        if not self.image:
            self.log.error("_load(): Unable to load room image: {0}".format(self.vars["image"]))
            return False

        # Music is defined for this view.
        if "music" in self.vars:
            self.music = self.vars["music"]

            # A file is named. Attempt to play it, if not already playing.
            if type(self.music) is str:
                if self.app.audio.playing_music != self.music:
                    self.app.audio.play_music(self.music)

            # The music was null, or a number of seconds to fade, so we are stopping all music.
            elif type(self.music) in [None, int, float]:
                self.app.audio.stop_music(self.music)

        # Calculate the exits for this roomview.
        self.__calculate_all_exits()

        # Success.
        self.log.info("_load(): Finished loading room: {0}".format(self.file))
        return True

    def __calculate_all_exits(self) -> bool:
        """Calculate the presence and destination of every potential named exit and go action exit in this roomview.

        Processing is handed off to _calculate_exit() for each exit. The information is stored in the self.exits
        variable for named exits, and the self.action_exits variable for go action exits.

        :return: True if succeeded, False if failed.
        """
        # Calculate each named exit in the view, adding it to the list of exits if it is present.
        if "exits" in self.vars:
            for e in self.vars["exits"]:
                thisexit = self.vars["exits"][e]
                dest = self.__calculate_exit(thisexit)
                if dest:
                    self.exits[e] = dest

        # Calculate each action exit in the room, adding it to the list of action exits if it is present.
        if "actions" in self.vars:
            for a in self.vars["actions"]:
                for act_type in ["go", "look", "use"]:
                    if act_type in a and a[act_type]["result"] == "exit":
                        thisexit = a[act_type]["contents"]
                        dest = self.__calculate_exit(thisexit)
                        if dest:
                            if tuple(a["rect"]) not in self.action_exits:
                                self.action_exits[tuple(a["rect"])] = {}
                            self.action_exits[tuple(a["rect"])][act_type] = dest

        # Done.
        return True

    def __calculate_exit(self, thisexit: dict) -> [str, None]:
        """Calculate the presence and destination of a potential exit in this roomview.
        
        Taking into account chance and funvalue_constraints conditionals for presence and destination the exit,
        calculate the actual destination (and presence or lack thereof). A string destination is returned if the exit
        is present, otherwise None is returned.

        :param thisexit: A dictionary containing an exit description section from the roomview.

        :return: Destination string if the exit should be present, otherwise None.
        """
        # If the exit name maps to a string, this is a simple, static exit.
        if type(thisexit) is str:
            return thisexit
        # If the exit name maps to a dictionary, this is a dynamic exit that needs to be calculated.
        elif type(thisexit) is dict:
            # If the "presence" section exists, there are variables affecting whether this exit will appear.
            if "presence" in thisexit:
                # First check for a chance-based probability, and keep or skip the exit accordingly.
                if "chance" in thisexit["presence"]:
                    chance_roll = random.randint(1, 1000)
                    if chance_roll < 1000 * thisexit["presence"]["chance"]:
                        pass  # Keep this exit.
                    else:
                        return None  # Skip this exit.
                # Next check for funvalue constraints, and keep or skip the exit accordingly.
                if "funvalue" in thisexit["presence"]:
                    constraint = thisexit["presence"]["funvalue"]
                    # Check a range constraint.
                    if constraint[0] == "range":
                        if constraint[1] > self.world.funvalue or constraint[2] < self.world.funvalue:
                            return None  # Skip this exit.
                    # Check an equality constraint.
                    elif constraint[0] == "=":
                        if self.world.funvalue != constraint[1]:
                            return None  # Skip this exit.
                    # Check a less than constraint.
                    elif constraint[0] == "<":
                        if not (self.world.funvalue < constraint[1]):
                            return None  # Skip this exit.
                    # Check a greater than constraint.
                    elif constraint[0] == ">":
                        if not (self.world.funvalue > constraint[1]):
                            return None  # Skip this exit.
                    # Check a less than or equal to constraint.
                    elif constraint[0] == "<=":
                        if not (self.world.funvalue <= constraint[1]):
                            return None  # Skip this exit.
                    # Check a greater than or equal to constraint.
                    elif constraint[0] == ">=":
                        if not (self.world.funvalue >= constraint[1]):
                            return None  # Skip this exit.
            # Next calculate the destination itself.
            # If the "destination" section maps to a string, the destination is static.
            if type(thisexit["destination"]) is str:
                return thisexit["destination"]
            # If the "destination" section maps to a dictionary, the destination is dynamic.
            elif type(thisexit["destination"]) is dict:
                # Start with the default destination and then see if it needs to be overwritten.
                dest = thisexit["destination"]["default"]
                # First check for a chance-based selector.
                if "chance" in thisexit["destination"]:
                    for constraint in thisexit["destination"]["chance"]:
                        chance_roll = random.randint(1, 1000)
                        if chance_roll < 1000 * constraint[0]:
                            dest = constraint[1]  # Select this alternate destination.
                # Next check for a funvalue selector.
                if "funvalue" in thisexit["destination"]:
                    for constraint in thisexit["destination"]["funvalue"]:
                        # Check a range constraint.
                        if constraint[0] == "range":
                            if constraint[1] <= self.world.funvalue <= constraint[2]:
                                dest = constraint[3]  # Select this alternate destination.
                        # Check an equality constraint.
                        elif constraint[0] == "=":
                            if self.world.funvalue == constraint[1]:
                                dest = constraint[2]  # Select this alternate destination.
                        # Check a less than constraint.
                        elif constraint[0] == "<":
                            if self.world.funvalue < constraint[1]:
                                dest = constraint[2]  # Select this alternate destination.
                        # Check a greater than constraint.
                        elif constraint[0] == ">":
                            if self.world.funvalue > constraint[1]:
                                dest = constraint[2]  # Select this alternate destination.
                        # Check a less than or equal to constraint.
                        elif constraint[0] == "<=":
                            if self.world.funvalue <= constraint[1]:
                                dest = constraint[2]  # Select this alternate destination.
                        # Check a greater than or equal to constraint.
                        elif constraint[0] == ">=":
                            if self.world.funvalue >= constraint[1]:
                                dest = constraint[2]  # Select this alternate destination.
                # Set the destination to whatever we landed on.
                return dest
