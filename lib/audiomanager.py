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
    """The Audio Manager

        This class manages the audio subsystem and allows playing sound effects and music.

        Attributes:
            driftwood: Base class instance.
            playing_music: Whether we are currently playing music or not.
            playing_sfx: Whether we are currently playing sfx or not.
    """

    def __init__(self, config):
        self.config = config
        self.log = Logger("Audio")

        self.playing_music = False
        self.playing_sfx = False

        self.__music = None
        self.__sfx = {}  # self.__sfx[id(Channel)] = {channel: pygame.mixer.Channel, filename: str}
        self.__iter_lock = False

        pygame.mixer.init()
        self.log.info("Initialized audio mixer.")

    def play_sfx(self, filename: str, volume: float = None, loop: Optional[int] = 0,
                 fade: float = 0.0) -> int:
        """Load and play a sound effect from an audio file.

        Args:
            filename: Filename of the sound effect.
            volume: Overrides the sfx_volume in the config for this sound effect. 0-128
            loop: Number of times to loop the audio. 0 for none, None for infinite.
            fade: If set, number of seconds to fade in sfx.

        Returns:
            Channel number if succeeded, None if failed.
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
        channel = sfx_temp.play()
        self.__sfx[id(channel)] = {"channel": channel, "filename": filename}
        self.playing_sfx = True
        return id(channel)

    def get_pygame_channel(self, channel_id: int) -> pygame.mixer.Channel:
        return self.__sfx[channel_id]["channel"]

    def get_pygame_music(self) -> pygame.mixer.music:
        return pygame.mixer.music

    def volume_sfx(self, channel_id: int = None, volume: float = None) -> Optional[float]:
        """Get or adjust the volume of a sound effect channel.

        Args:
            channel_id: Audio channel of the sound effect whose volume to adjust or query. None adjusts all channels.
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded (average volume of sfx if no channel is passed), None if failed.
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
            self.log.error("volume_sfx: sound and volume cannot both be None.")
            return None

    def volume_sfx_by_filename(self, filename: str, volume: float = None) -> Optional[float]:
        """Get or adjust the volume of all currently playing instances of the named sound effect.

        Args:
            filename: Filename of the sound effect whose volume to adjust or query.
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded, None if failed.
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
        self.log.warn("volume_sfx_by_filename: no sound with this filename currently playing: {0}".format(filename))
        return None

    def stop_sfx(self, channel_id: int, fade: float = 0.0) -> bool:
        """Stop a sound effect. Requires the sound effect's channel number from play_sfx()'s return code.

        Args:
            channel_id: Audio channel of the sound effect to stop.
            fade: If set, number of seconds to fade out sfx.

        Returns:
            True if succeeded, false if failed.
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
            self.log.warn("stop_sfx: already stopped or nonexistent channel: {0}".format(channel_id))
            return False

    def stop_sfx_by_filename(self, filename: str, fade: float = 0.0) -> bool:
        """Stop all currently playing instances of the named sound effect.

        Args:
            filename: Filename of the sound effect instances to stop.
            fade: If set, number of seconds to fade out sfx.

        Returns:
            True if succeeded, false if failed.
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
            self.log.warn("stop_sfx_by_filename: cannot stop nonexistent instances of sfx: {0}".format(filename))
        return result

    def stop_all_sfx(self) -> bool:
        """Stop all currently playing sound effects.

        Returns:
            True
        """
        self.__iter_lock = True
        sfx_temp = self.__sfx.copy()
        for sfx in sfx_temp:
            self.stop_sfx(sfx)
        self.__iter_lock = False
        self.__sfx = {}
        return True

    def play_music(self, filename: str, volume: float = None, loop: int = 0, start: float = 0.0, fade: int = 0) -> bool:
        """Load and play music from an audio file. Also stops and unloads any previously loaded music.

        Args:
            filename: Filename of the music.
            volume: Overrides the music_volume in the config for this music. 0-128
            loop: Number of times to loop the audio. 0 for none, None for infinite.
            fade: If set, number of seconds to fade in music.

        Returns:
            True if succeeded, False if failed.
        """
        # Stop and unload any previously loaded music.
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

        self.playing_music = True

        return True

    def volume_music(self, volume: float = None) -> Optional[float]:
        """Get or adjust the volume of the currently playing music.

        Args:
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded, None if failed.
        """
        if self.playing_music:
            if volume is not None:
                pygame.mixer.music.set_volume(volume)
                return volume
            else:  # Get the volume.
                return pygame.mixer.music.get_volume()

        self.log.warn("volume_music: cannot adjust volume for nonexistent music")
        return None

    def stop_music(self, fade: int = None) -> bool:
        """Stop and unload any currently loaded music.

        Args:
            fade: If set, number of seconds to fade out the music.

        Returns:
            True if succeeded, False if failed.
        """
        if not self.__music:
            self.log.warn("stop_music: no music currently playing")
            return False

        if pygame.mixer.music.get_busy():
            if not fade:  # Stop the music.
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self.__music = None
                self.playing_music = False
            else:  # Fade out the music.
                pygame.mixer.music.fadeout(fade)
                # Cleanup callback will handle deletion.

        return True

    def _cleanup(self) -> None:
        # Tick callback to clean up files we're done with.
        if self.__music and not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            self.__music = None
            self.playing_music = False
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
