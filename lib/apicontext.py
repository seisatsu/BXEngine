#####################
# BXEngine          #
# apicontext.py     #
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

from typing import Any

from lib.logger import Logger


class APIContext(object):
    """The API Context

    An instance of this class is given to each event script as an access point to the engine API.

    :ivar this: The filename of the currently executing event script.
    :ivar app: The main App instance.
    :ivar audio: The AudioManager instance.
    :ivar cursor: The Cursor instance.
    :ivar log: The Logger instance for this script.
    :ivar resource: The ResourceManager instance.
    :ivar room: The current Room instance.
    :ivar script: The ScriptManager instance.
    :ivar ui: The UI instance.
    :ivar world: The World instance.
    :ivar vars: The vars variable from the main App, used to share variables between event scripts.
    """

    def __init__(self, filename, app, audio, cursor, resource, script, ui, world):
        """APIContext Class Initializer

        :param filename: The filename of the currently executing event script.
        :param app: The main App instance.
        :param audio: The AudioManager instance.
        :param cursor: The Cursor instance.
        :param resource: The ResourceManager instance.
        :param script: The ScriptManager instance.
        :param ui: The UI instance.
        :param world: The World instance.
        """
        self.this = filename
        self.app = app
        self.audio = audio
        self.cursor = cursor
        self.log = Logger(filename)
        self.resource = resource
        self.room = world.room
        self.script = script
        self.ui = ui
        self.world = world
        self.vars = app.vars

    def __contains__(self, item: str) -> bool:
        return item in self.vars

    def __getitem__(self, item: str) -> Any:
        if not self.__contains__(item):
            return None
        return self.vars[item]
