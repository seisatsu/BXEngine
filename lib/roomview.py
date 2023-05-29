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
        self.vars = None
        self.image = None
        self.music = None
        self.exits = None
        self.action_exits = None
        self.log = Logger("Roomview")

    def _load(self) -> bool:
        """Load the room descriptor JSON file. Also load the room image.

        :return: True if succeeded, False if failed.
        """
        # Attempt to load the room file.
        self.log.info("Loading room and view: {0}:{1}".format(self.file, self.view))
        whole_room = self.resource.load_json(self.file, "room")

        # We were unable to load the room file.
        if not whole_room:
            self.log.error("Unable to load room descriptor: {0}".format(self.file))
            return False

        # Make sure the view we are loading exists.
        if self.view not in whole_room:
            self.log.error("No such view in room: {0}: {1}".format(self.file, self.view))
            return False

        # Load the requested view.
        self.vars = whole_room[self.view]

        # Attempt to load the view's background image.
        self.image = self.resource.load_image(self.vars["image"], self.config["window"]["size"])

        # We were unable to load the background image.
        if not self.image:
            self.log.error("Unable to load room image: {0}".format(self.vars["image"]))
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

        # Success.
        self.log.info("Finished loading room: {0}".format(self.file))
        return True

    def _calculate_exits(self) -> bool:
        """Calculate the presence and destination of each potential exit in this roomview.
        
        Taking into account chance and funvalue_constraints conditionals for presence and destination of each named
        exit and each go action exit, calculate the actual destinations (and presence or lack thereof) for each exit.
        This information is placed into the self.exits and self.action_exits dictionaries.
        """
        pass