#####################
# BXEngine          #
# audiomanager.py   #
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
from lib.util import normalize_path


class AudioManager:
    """
    This class manages the audio subsystem and allows playing sound effects and music.

    :ivar config: This contains the engine's configuration variables.
    :ivar log: The Logger instance for this class.
    :ivar playing_music: If music is currently playing, this contains the filename; otherwise it is None.
    :ivar playing_sfx: True if any sound effects are currently playing, otherwise False.
    :ivar __sfx: This private variable is a dict of Channel IDs mapped to a PyGame Mixer Channel and the Filename.
    :ivar __iter_lock: This private variable is true when __sfx is being iterated within a method of this class,
                       to prevent the _cleanup method from deleting __sfx members during iteration.
    """

    def __init__(self, config):
        """The AudioManager Class

        :param config: The engine's configuration variables.
        """
        self.config = config
        self.log = Logger("Audio")

        self.playing_music = None
        self.playing_sfx = False

        self.__sfx = {}  # self.__sfx[id(Channel)] = {channel: pygame.mixer.Channel, filename: str}
        self.__iter_lock = False

        # Initialize the PyGame Mixer, which we are an abstraction of.
        pygame.mixer.init()
        self.log.info("Initialized audio mixer.")

    def play_sfx(self, filename: str, volume: float = None, loop: Optional[int] = 0,
                 fade: float = 0.0) -> int:
        """Load and play a sound effect from an audio file.

        :param filename: The filename of the audio file to play.
        :param volume: Use the current volume if None, otherwise set the new volume. Takes a float between 0.0 and 1.0.
        :param loop: If 0, only play once. If -1, loop forever. If > 0, replay this many times. (1 plays twice, etc.)
        :param fade: Time to fade in the sound effect.
        :return: A unique identifier for this sound effect's channel. This is used as an argument to other methods.
        """
        filename = normalize_path(filename)
        if filename.startswith("$COMMON$/"):
            fullpath = "{0}/{1}".format("common", filename.split('/', 1)[1])
        else:
            fullpath = "{0}/{1}".format(self.config["world"], filename)
        sfx_temp = pygame.mixer.Sound(fullpath)
        if volume:
            sfx_temp.set_volume(volume)
        else:
            sfx_temp.set_volume(self.config["audio"]["sfx_volume"])
        channel = sfx_temp.play(loop, 0, int(fade*1000))
        self.__sfx[id(channel)] = {"channel": channel, "filename": filename}
        self.playing_sfx = True
        return id(channel)

    def get_pygame_channel(self, channel_id: int) -> pygame.mixer.Channel:
        """Get the raw PyGame Mixer Sound channel for a sound effect.

        :param channel_id: The abstracted channel ID given by play_sfx().
        :return: The raw PyGame Mixer channel for this sound effect.
        """
        return self.__sfx[channel_id]["channel"]

    def get_pygame_music(self) -> pygame.mixer.music:
        """Get the raw PyGame Mixer Music object for the current music.

        :return: The raw PyGame Mixer Music object for the current music.
        """
        return pygame.mixer.music

    def volume_sfx(self, channel_id: int = None, volume: float = None) -> Optional[float]:
        """
        Get or adjust the volume of a sound effect channel.
        """
        # Search for the sound effect.
        if channel_id is not None and volume is not None:
            if channel_id in self.__sfx:
                # Set the volume.
                self.__sfx[channel_id]["channel"].set_volume(volume)
                return volume
        elif channel_id is not None and volume is None:
            if channel_id in self.__sfx:
                return self.__sfx[channel_id]["channel"].get_volume()
        elif channel_id is None and volume is not None:
            self.__iter_lock = True
            for chtmp in self.__sfx:
                self.__sfx[chtmp]["channel"].set_volume(volume)
            self.__iter_lock = False
            return volume
        else:
            self.log.error("volume_sfx(): Sound and volume cannot both be None.")
            return None

    def volume_sfx_by_filename(self, filename: str, volume: float = None) -> Optional[float]:
        """
        Get or adjust the volume of all currently playing instances of the named sound effect.
        """
        result = None
        self.__iter_lock = True
        for channel_id in self.__sfx:
            if self.__sfx[channel_id]["filename"] == filename:
                if volume is not None:
                    self.__sfx[channel_id]["channel"].set_volume(volume)
                    result = volume
                else:
                    return self.__sfx[channel_id]["channel"].get_volume()
        self.__iter_lock = False
        if result:
            return result
        self.log.warn("volume_sfx_by_filename(): No sound with this filename currently playing: {0}".format(filename))
        return None

    def stop_sfx(self, channel_id: int, fade: float = 0.0) -> bool:
        """
        Stop a sound effect. Requires the sound effect's channel number from play_sfx()'s return code.
        """
        if channel_id in self.__sfx:
            if self.__sfx[channel_id]["channel"].get_busy():
                if not fade:  # Stop channel.
                    self.__sfx[channel_id]["channel"].stop()
                    del self.__sfx[channel_id]
                else:  # Fade out channel.
                    self.__sfx[channel_id]["channel"].fadeout(fade)
                    # Cleanup callback will handle deletion.
            return True
        else:
            self.log.warn("stop_sfx(): Already stopped or nonexistent channel: {0}".format(channel_id))
            return False

    def stop_sfx_by_filename(self, filename: str, fade: float = 0.0) -> bool:
        """
        Stop all currently playing instances of the named sound effect.
        """
        result = False
        self.__iter_lock = True
        for channel_id in self.__sfx:
            if self.__sfx[channel_id]["filename"] == filename:
                if fade:
                    self.__sfx[channel_id]["channel"].fadeout(fade)
                else:
                    self.__sfx[channel_id]["channel"].stop()
                    del self.__sfx[channel_id]
                result = True
        self.__iter_lock = False

        if not result:
            self.log.warn("stop_sfx_by_filename(): Cannot stop nonexistent instances of sfx: {0}".format(filename))
        return result

    def stop_all_sfx(self) -> bool:
        """
        Stop all currently playing sound effects.
        """
        self.__iter_lock = True
        sfx_temp = self.__sfx.copy()
        for sfx in sfx_temp:
            self.stop_sfx(sfx)
        self.__iter_lock = False
        self.__sfx = {}
        return True

    def fadeout_all_sfx(self, fade: float) -> bool:
        """

        :param fade:
        :return:
        """

    def play_music(self, filename: str, volume: float = None, loop: int = 0, start: float = 0.0, fade: int = 0) -> bool:
        """
        Load and play music from an audio file. Also stops and unloads any previously loaded music.
        """
        # Stop and unload any previously loaded music.
        if self.playing_music:
            self.stop_music()

        filename = normalize_path(filename)
        if filename.startswith("$COMMON$/"):
            fullpath = "{0}/{1}".format("common", filename.split('/', 1)[1])
        else:
            fullpath = "{0}/{1}".format(self.config["world"], filename)

        pygame.mixer.music.load(fullpath)

        if loop is None:
            loop = -1

        pygame.mixer.music.play(loop, start, fade)

        if volume is not None:
            pygame.mixer.music.set_volume(volume)
        else:
            pygame.mixer.music.set_volume(self.config["audio"]["music_volume"])

        self.playing_music = filename

        return True

    def volume_music(self, volume: float = None) -> Optional[float]:
        """
        Get or adjust the volume of the currently playing music.
        """
        if self.playing_music:
            if volume is not None:
                pygame.mixer.music.set_volume(volume)
                return volume
            else:  # Get the volume.
                return pygame.mixer.music.get_volume()

        self.log.warn("volume_music(): Cannot adjust volume for nonexistent music.")
        return None

    def stop_music(self, fade: int = None) -> bool:
        """
        Stop and unload any currently loaded music.
        """
        if not self.playing_music:
            self.log.warn("stop_music(): No music currently playing.")
            return False

        if pygame.mixer.music.get_busy():
            if not fade:  # Stop the music.
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self.playing_music = None
            else:  # Fade out the music.
                pygame.mixer.music.fadeout(fade)
                # Cleanup callback will handle deletion.

        return True

    def _cleanup(self) -> None:
        """
        Tick callback to clean up files we're done with.
        """
        if self.playing_music and not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            self.playing_music = None
        try:
            if not len(self.__sfx):
                self.playing_sfx = False
            else:
                for sfx in self.__sfx:
                    if not self.__sfx[sfx]["channel"].get_busy():
                        if not self.__iter_lock:
                            del self.__sfx[sfx]
        except RuntimeError:
            pass
