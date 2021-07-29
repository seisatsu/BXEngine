#####################
# BXEngine          #
# room.py           #
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

import pygame

from lib.util import resource_path


class Room(object):
    """
    A class to represent the current room.
    """

    def __init__(self, config, world, room_file):
        self.config = config
        self.world = world
        self.file = room_file
        self.vars = None
        self.image = None

    def load(self):
        """
        Load the room descriptor JSON file. Also load the room image.
        """
        with open("{0}/{1}".format(self.world.dir, self.file)) as f:
            self.vars = json.load(f)
        self.image = pygame.transform.scale(pygame.image.load(
            resource_path("{0}/{1}".format(self.world.dir, self.vars["image"]))), self.config["window"]["size"])
