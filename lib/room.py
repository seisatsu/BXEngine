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

from typing import Optional

import pygame

from lib.logger import Logger


class Room(object):
    """A class to represent the current room.

    :ivar config: This contains the engine's configuration variables.
    :ivar app: The main App instance.
    :ivar world: The World instance.
    :ivar resource: The ResourceManager instance.
    :ivar file: The filename of the room.
    :ivar vars: The JSON object representing the room file.
    :ivar image: The background image for this room.
    :ivar music: The music file loaded for this room, if any.
    :ivar log: The Logger instance for this class.
    :ivar overlays: A dict of Overlay IDs mapped to overlays currently in the room.
    """

    def __init__(self, config, app, world, resource, room_file):
        """The Room initializer.

        :param config: This contains the engine's configuration variables.
        :param app: The main App instance.
        :param world: The World instance.
        :param resource: The ResourceManager instance.
        :param room_file: The filename of the room.
        """
        self.config = config
        self.app = app
        self.world = world
        self.resource = resource
        self.file = room_file
        self.vars = None
        self.image = None
        self.music = None
        self.log = Logger("Room")

        # A dict of Overlay IDs mapped to overlays currently in the room.
        # self.overlays[Overlay_ID] = {"filename": filename, "image": pygame.Surface, "position": [x, y]}
        self.overlays = {}

    def insert_overlay(self, imagefile: [str, pygame.Surface], position: tuple[int, int],
                       scale: tuple[int, int] = None) -> Optional[int]:
        """Insert an overlay image into the room.
        """
        # Attempt to load the overlay image from a filename.
        if type(imagefile) is str:
            overlay_image = self.resource.load_image("{0}/{1}".format(self.world.dir, imagefile), scale)
            filename = imagefile

        # We were passed a surface pre-loaded from ResourceManager.
        elif type(imagefile) is pygame.Surface:
            overlay_image = imagefile
            if scale:
                overlay_image = pygame.transform.scale(overlay_image, scale)
            filename = None

        # We don't know what this is.
        else:
            self.log.error("insert_overlay(): Invalid image given.")
            return False

        # We were unable to load the background image.
        if not overlay_image:
            self.log.error("insert_overlay(): Unable to load overlay image: {0}".format(overlay_image))
            return None

        # Success.
        self.overlays[id(overlay_image)] = {"filename": filename, "image": overlay_image, "position": position}
        self.app._render()
        self.log.info("insert_overlay(): Added overlay image: {0} at position: {1}".format(overlay_image, position))
        return id(overlay_image)

    def remove_overlay(self, overlay_id: int) -> bool:
        """Remove an overlay image from the room."""
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("remove_overlay(): Overlay ID does not exist to remove: ".format(overlay_id))
            return False

        # Success.
        del self.overlays[overlay_id]
        self.app._render()
        self.log.info("remove_overlay(): Removed overlay image with ID: {0}".format(overlay_id))
        return True

    def reposition_overlay(self, overlay_id: int, position: tuple[int, int]) -> bool:
        """Reposition an overlay image on the window.
        """
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("reposition_overlay(): Overlay ID does not exist to reposition: ".format(overlay_id))
            return False

        # Success.
        self.overlays[overlay_id]["position"] = position
        self.app._render()
        self.log.info("reposition_overlay(): Repositioned overlay image with ID: {0} to position: {1}".format(
            overlay_id, position))
        return True

    def rescale_overlay(self, overlay_id: int, scale: tuple[int, int]) -> bool:
        """Rescale an overlay image.
        """
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("rescale_overlay(): Overlay ID does not exist to rescale: ".format(overlay_id))
            return False

        # Success.
        self.overlays[overlay_id]["image"] = pygame.transform.scale(self.overlays[overlay_id]["image"], scale)
        self.app._render()
        self.log.info("reposition_overlay(): Rescaled overlay image with ID: {0} to size: {1}".format(
            overlay_id, scale))
        return True

    def _load(self) -> bool:
        """Load the room descriptor JSON file. Also load the room image.

        :return: True if succeeded, False if failed.
        """
        # Attempt to load the room file.
        self.log.info("Loading room: {0}".format(self.file))
        self.vars = self.resource.load_json(self.file, "room")

        # We were unable to load the room file.
        if not self.vars:
            self.log.error("Unable to load room descriptor: {0}".format(self.file))
            return False

        # Attempt to load the room's background image.
        self.image = self.resource.load_image(self.vars["image"], self.config["window"]["size"])

        # We were unable to load the background image.
        if not self.image:
            self.log.error("Unable to load room image: {0}".format(self.vars["image"]))
            return False

        # Music is defined for this room.
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
