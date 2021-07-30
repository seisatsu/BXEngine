#####################
# BXEngine          #
# scriptmanager.py  #
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

import importlib.util
import os
import traceback
from typing import Any, Optional

from lib.logger import Logger


class ScriptManager:
    """The Script Manager

    This class handles loading scripts and calling their functions. It defines its own method for retrieving the
    script file (independent of ResourceManager) and internally caches it forever.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self):
        """
        ScriptManager class initializer.
        """
        self.log = Logger("script")

        # Dictionary of module instances mapped by filename.
        self.__modules = {}

    def __contains__(self, item: str) -> bool:
        return self._module(item) is not None

    def __getitem__(self, item: str) -> Any:
        ret = self._module(item)
        if ret not in [None, False]:
            return ret
        elif ret is False:
            self.log.error("no such module: {0}".format(item))
        else:
            self.log.error("error from module: {0}".format(item))
        return None

    def call(self, filename: str, func: str, *args: Any) -> Any:
        """Call a function from a script, loading if not already loaded.

        Usually you just want to run "Driftwood.script[path].function(args)". This wraps around that, and is cleaner
        for the engine to use in most cases. It also prevents exceptions from raising into the engine scope and
        crashing it, so the engine will always call scripts through this method.

        Args:
            filename: Filename of the python script containing the function.
            func: Name of the function to call.
            args: Arguments to pass.

        Returns:
            Function return code if succeeded, None if failed.
        """
        try:
            return getattr(self[filename], func)(*args)
        except:
            self.log.error("call: error from function: {0}: {1}\n{2}".format(filename, func + "()",
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

        Args:
            filename: Filename of the python script whose module instance should be returned.

        Returns: Python module instance if succeeded, False if nonexistent, or None if error.
        """
        if filename not in self.__modules:
            return self.__load(filename)
        else:
            return self.__modules[filename]

    def __load(self, filename: str) -> Optional[bool]:
        """Load a script.

        Args:
            filename: Filename of the python script to load.
        """
        if not os.path.exists(filename):
            self.log.error("__load: no such script: {0}".format(filename))
            return False

        mname = os.path.splitext(os.path.split(filename)[-1])[0]

        try:
            # Build the module.
            spec = importlib.util.spec_from_file_location(mname, filename)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.__modules[filename] = mod

            self.log.info("loaded: {0}".format(filename))
            return True

        except:
            self.log.error("__load: error from script: {0}\n{1}".format(filename, traceback.format_exc(10).rstrip()))
            return None
