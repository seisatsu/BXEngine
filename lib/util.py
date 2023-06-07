##################
# BXEngine       #
# util.py        #
# Copyright 2021 #
# Sei Satzparad  #
##################

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

import functools
import sys
import types

from typing import Callable

from lib.logger import Logger


def normalize_path(path: str) -> str:
    """Normalize paths between Windows and other systems.

    :param path: The path to be normalized.
    """
    new_path = path.replace('\\', '/')
    if "../" in new_path:
        Logger("Util").critical("normalize_path(): Detected illegal upward traversal attempt: {0}".format(new_path))
        sys.exit(10)
    return new_path


def copy_function(f: Callable) -> Callable:
    """Deep copy a function.

    Based on https://stackoverflow.com/a/6528148/190597 (Glenn Maynard)

    This is needed to pass the same function multiple times to TickManager as a callback.

    :param f: The function to be copied.

    :return: A function object.
    """
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g
