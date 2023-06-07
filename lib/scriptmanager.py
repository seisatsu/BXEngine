####################
# BXEngine         #
# scriptmanager.py #
# Copyright 2021   #
# Sei Satzparad    #
####################

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

import importlib.util
import os
import sys
import traceback
from typing import Any, Optional

from lib.apicontext import APIContext
from lib.logger import Logger
from lib.util import normalize_path


class ScriptManager:
    """The Script Manager

    This class handles loading scripts and calling their functions. It defines its own method for retrieving the
    script file (independent of ResourceManager) and internally caches it forever.

    :ivar log: The Logger instance for this class.
    :ivar app: The base application instance.
    :ivar audio: The AudioManager instance.
    :ivar cursor: The Cursor instance.
    :ivar resource: The ResourceManager instance.
    :ivar ui: The UIManager instance.
    :ivar world: The World instance.
    :ivar __modules: The dictionary of active module instances mapped by filename.
    """

    def __init__(self, app, audio, cursor, resource, ui, world):
        """ScriptManager class initializer.

        :param app: The base application instance.
        :param audio: The AudioManager instance.
        :param cursor: The Cursor instance.
        :param resource: The ResourceManager instance.
        :param ui: The UIManager instance.
        :param world: The World instance.
        """
        self.log = Logger("script")
        self.app = app
        self.audio = audio
        self.cursor = cursor
        self.resource = resource
        self.ui = ui
        self.world = world

        # Dictionary registry of module instances mapped by filename.
        self.__modules = {}

    def __contains__(self, item: str) -> bool:
        return self._module(item) is not None

    def __getitem__(self, item: str) -> Any:
        ret = self._module(item)
        if ret not in [None, False]:
            return ret
        elif ret is False:
            self.log.error("__getitem__(): No such module: {0}".format(item))
        else:
            self.log.error("__getitem__(): Error from module: {0}".format(item))
        return None

    def call(self, filename: str, func: str, *args: Any) -> Any:
        """Call a function from a script, loading if not already loaded.

        Usually you just want to run "BXE.script[path].function(args)". This wraps around that, and is cleaner
        for the engine to use in most cases. It also prevents exceptions from raising into the engine scope and
        crashing it, so the engine will always call scripts through this method.

        :param filename: Filename of the python script containing the function.
        :param func: Name of the function to call.
        :param args: Arguments to pass.

        :return: Function return code if succeeded, None if failed.
        """
        # Normalize the path across operating systems to always use forward slashes.
        filename = normalize_path(filename)

        # Call the module function from our registry if it can be loaded or is loaded already.
        try:
            return getattr(self[filename], func)(*args)

        # Give an error if we are attempting to call a module that could not be loaded.
        except AttributeError:
            self.log.error("call(): Module not loaded for call: {0}: {1}".format(filename, func + "()"))
            return None

        # Exit with a critical error if the module called sys.exit().
        except SystemExit:
            self.log.critical("call(): Script called sys.exit(): {0}\n{1}".format(
                filename, traceback.format_exc(10).rstrip()))
            sys.exit(11)

        # If the module gave an error, record it.
        except:
            self.log.error("call(): Error from function: {0}: {1}\n{2}".format(filename, func + "()",
                                                                               traceback.format_exc().rstrip()))
            return None

    # _module() returns an Any rather than Optional[module] because the latter results in a NameError.
    #
    # Python user bjs says:
    # "there is a module type in python but i have a feeling that [forgetting to allow it in type annotations] was a
    # oversight when the typehint / typechecking peps were being written"
    def _module(self, filename: str) -> Any:
        """Return the module instance of a script, loading if not already loaded.

        This method is not crash-safe. If you call a method in a module you got from this function, errors will
        not be caught and the engine will crash if a problem occurs. This is mostly used internally by ScriptManager
        to load a module or check if one exists.

        :param filename: Filename of the python script whose module instance should be returned.

        :return: Python module instance if succeeded, False if nonexistent, or None if error.
        """
        # Normalize the path across operating systems to always use forward slashes.
        filename = normalize_path(filename)

        # Load the module if not loaded and then return it, otherwise return the existing module.
        if filename not in self.__modules:
            return self.__load(filename)
        else:
            return self.__modules[filename]

    def __load(self, filename: str) -> Optional[bool]:
        """Load a script.

        :param filename: Filename of the python script to load.

        :return: Python module instance if succeeded, False if nonexistent, or None if error.
        """
        # Normalize the path across operating systems to always use forward slashes.
        filename = normalize_path(filename)

        # Determine the full path of the module.
        if filename.startswith("$COMMON$/"):
            fullpath = "{0}/{1}".format("common", filename.split('/', 1)[1])
        else:
            fullpath = "{0}/{1}".format(self.world.dir, filename)

        # If the path does not exist, give an error.
        if not os.path.exists(fullpath):
            self.log.error("__load(): No such script: {0}".format(fullpath))
            return False

        # Determine the appropriate name of the module.
        mname = os.path.splitext(os.path.split(filename)[-1])[0]

        # Build the module into memory from a file and load it into our registry.
        try:
            spec = importlib.util.spec_from_file_location(mname, fullpath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.__modules[filename] = mod
            self.__modules[filename].BXE = APIContext(filename, self.app)

            self.log.info("__load(): Loaded script: {0}".format(filename))
            return self.__modules[filename]

        # Exit with a critical error if the module called sys.exit().
        except SystemExit:
            self.log.critical("__load(): Script called sys.exit(): {0}\n{1}".format(
                filename, traceback.format_exc(10).rstrip()))
            sys.exit(11)

        # If the module gave an error, record it.
        except:
            self.log.error("__load(): Error from script: {0}\n{1}".format(filename, traceback.format_exc(10).rstrip()))
            return None
