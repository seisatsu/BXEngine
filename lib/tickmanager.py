#######################
# BXEngine            #
# tickmanager.py      #
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

import pygame

from lib.logger import Logger


class TickManager:
    """The Tick Manager

    This class tracks game ticks and manages delayed events through a callback registry.

    :ivar log: The Logger instance for this class.
    :ivar registry: The registry of timed event callbacks.
    """
    def __init__(self):
        """
        TickManager class initializer.
        """
        self.log = Logger("Tick")

        self.registry = {}  # {callback: {start_time: int, delay: int, continuous: bool}}

    def register(self, callback: object, delay: int, continuous: bool = False) -> bool:
        """Register a timed event callback.

        The registered event is a function that will be called, perhaps repeatedly, after a set interval in
        milliseconds. (Each function can only be registered once, so you would need to copy its object to register it
        a second time.)

        :param callback: A function to be called when the event comes due.
        :param delay: The delay in milliseconds until the event comes due.
        :param continuous: Whether the event should keep being called at the same interval or be deleted after one call.
        """
        # If this callback is already in the registry, fail.
        if callback in self.registry:
            self.log.error("register(): Attempt to register already registered callback: {0}".format(callback.__name__))
            return False

        # Otherwise, add it to the registry.
        self.registry[callback] = {"start_time": pygame.time.get_ticks(), "delay": delay, "continuous": continuous}
        self.log.info("register(): Registered callback: {0}".format(callback.__name__))

        # Success.
        return True

    def unregister(self, callback: object) -> bool:
        """Unregister a timed event callback.

        This takes the original function object as an argument, and unregisters that function's event.

        :param callback: The function of the event to be unregistered.
        """
        # If this callback is not in the registry, fail.
        if callback not in self.registry:
            self.log.error("unregister(): Attempt to unregister nonexistent callback: {0}".format(callback.__name__))
            return False

        # Otherwise, remove it from the registry.
        del self.registry[callback]
        self.log.info("register(): Unregistered callback: {0}".format(callback.__name__))

        # Success.
        return True

    def _tick(self) -> None:
        """This is called repeatedly by the mainloop.
        """
        # Loop through the registry and look for delayed events that have come due.
        for callback in self.registry:
            # The event is due if the correct amount of milliseconds has passed since the start_time.
            if pygame.time.get_ticks() - self.registry[callback]["start_time"] > self.registry[callback]["delay"]:
                # Call the callback.
                self.registry[callback]()
                # If the event is continuous, update its start time to the current time. Otherwise, delete it.
                if self.registry[callback]["continuous"]:
                    self.registry[callback]["start_time"] = pygame.time.get_ticks()
                else:
                    del self.registry[callback]
