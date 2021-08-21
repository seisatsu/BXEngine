#####################
# BXEngine          #
# cursor.py         #
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

import pygame


class Cursor(object):
    """A class to represent our mouse cursor.

    :ivar click: Whether a click is in progress. (Whether a recognized mouse button is depressed.)
    :ivar last_click: A unique ID for the last navigation region or action zone the mouse was depressed in.
    :ivar pos: The current position of the mouse cursor.
    :ivar nav: The navigation region the mouse cursor is currently in, if any.
    :ivar action: The JSON contents of the action zone the mouse cursor is currently in, if any.
    """

    def __init__(self):
        self.click = False
        self.last_click = None
        self.pos = [0, 0]
        self.nav = None
        self.action = None

    def _update(self) -> None:
        """Update the cursor position.
        """
        self.pos = pygame.mouse.get_pos()
