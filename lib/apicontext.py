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

import os
from typing import Any

from lib.logger import Logger


class APIContext(object):
    """The Event Scripting API Context

    A new instance of this class is given to each event script as an access point to the engine API.
    It is accessible via the "BXE" attribute given to every event script's main scope.
    For example, to access the AudioManager from an event script, its instance would be "BXE.audio".
    You can also access BXE like a dict, as a shorthand for "BXE.vars" which holds persistent variables.
    For example, "BXE['myvar']" is the same as "BXE.vars['myvar']".
    Note that class methods an event script should never call begin with an underscore.

    :ivar filename: The filename of the currently executing event script.
    :ivar app: The main App instance.
    :ivar audio: The AudioManager instance.
    :ivar cursor: The Cursor instance.
    :ivar database: The DatabaseManager instance.
    :ivar log: The Logger instance for this script.
    :ivar overlay: The OverlayManager instance.
    :ivar resource: The ResourceManager instance.
    :ivar script: The ScriptManager instance.
    :ivar ui: The UI instance.
    :ivar world: The World instance.
    :ivar vars: The vars variable from the main App, used to share variables between event scripts.
    :ivar path: The relative path to this script, from the engine's base directory.
    :ivar dir: The directory this script is in.
    """

    def __init__(self, filename, app):
        """APIContext Class Initializer

        :param filename: The filename of the currently executing event script.
        :param app: The main App instance.
        """
        self.filename = filename
        self.app = app
        self.audio = self.app.audio
        self.cursor = self.app.cursor
        self.database = self.app.database
        self.log = Logger(filename)
        self.overlay = self.app.overlay
        self.resource = self.app.resource
        self.script = self.app.script
        self.ui = self.app.ui
        self.world = self.app.world
        self.vars = self.app.vars
        self.path = os.path.join(self.world.dir, self.filename)
        self.dir = os.path.dirname(self.path)

    def __contains__(self, item: str) -> bool:
        return item in self.vars

    def __getitem__(self, item: str) -> Any:
        if not self.__contains__(item):
            return None
        return self.vars[item]
