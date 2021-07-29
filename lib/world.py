#####################
# BXEngine          #
# world.py          #
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

import json

from lib.room import Room


class World(object):
    """
    A class to represent the game world.
    """

    def __init__(self, config):
        self.config = config
        self.dir = self.config["world"]
        self.vars = None
        self.room = None

    def load(self):
        """
        Load the world descriptor JSON file.
        """
        with open("{0}/world.json".format(self.dir)) as f:
            self.vars = json.load(f)
        self.change_room(self.vars["first_room"])

    def navigate(self, direction):
        """
        Change rooms by exit name in the current room.
        """
        if direction in self.room.vars["exits"]:
            self.change_room(self.room.vars["exits"][direction])

    def change_room(self, room_file):
        """
        Change rooms by room descriptor filename.
        """
        self.room = Room(self.config, self, room_file)
        self.room.load()
