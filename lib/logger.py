#######################
# BXEngine            #
# logger.py           #
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

"""
Adapted from DennisMUD.
* https://github.com/seisatsu/DennisMUD/
"""

import datetime
import time
import traceback

from typing import Any

# Variables shared between all Logger instances.
_LOGFILE = None
_LOGLEVEL = None
_STDOUT = None
_WAITONCRITICAL = None
_SUPPRESSIONS = []


def init(config: dict) -> None:
    """Initialize the Logger system.

    This must be run before creating any Logger instances.
    It sets up global variables that are shared between all Loggers.

    :param config: This contains the engine's configuration variables.
    """
    global _LOGFILE, _LOGLEVEL, _STDOUT, _WAITONCRITICAL, _SUPPRESSIONS

    # Note that we are initializing the logger.
    print("Initializing logger...")

    # On Windows, we might not want to immediately close the console on a critical error.
    if "wait_on_critical" in config["log"]:
        _WAITONCRITICAL = config["log"]["wait_on_critical"]

    # Make sure the chosen log level is valid. Otherwise force the highest log level.
    if config["log"]["level"] not in ["critical", "error", "warn", "info", "debug"]:
        print(timestamp(), "[Logger#error] init(): Invalid log level in config, defaulting to \"debug\".")
        config["log"]["level"] = "debug"
    _LOGLEVEL = config["log"]["level"]

    # Give an error if no logging option is selected, and default to stdout.
    if "stdout" in config["log"]:
        if not config["log"]["stdout"] and not config["log"]["file"]:
            # No logging target is set, so force stdout.
            print(timestamp(), "[Logger#error] init(): No logging target in config, defaulting to stdout.")
            config["log"]["stdout"] = True
            _STDOUT = True
        elif config["log"]["stdout"]:
            _STDOUT = True
    else:
        _STDOUT = True

    # Try to open the log file. If this fails, give an error and default to stdout.
    if config["log"]["file"]:
        try:
            _LOGFILE = open(config["log"]["file"], 'a')
        except:
            if _LOGLEVEL in ["debug", "info", "warn", "error"]:
                print(timestamp(), "[Logger#error] init(): Could not open log file: {0}".format(
                    config["log"]["file"]))
                print(traceback.format_exc(1))
            if "stdout" in config["log"]:
                config["log"]["stdout"] = True
                _STDOUT = True

    # Store the list of suppressions.
    _SUPPRESSIONS = config["log"]["suppress"]

    # Note that we have finished initializing the logger.
    if _LOGLEVEL in ["debug", "info"]:
        if _STDOUT:
            print(timestamp(), "[Logger#info] init(): Finished initializing logger.")
        if _LOGFILE:
            _LOGFILE.write(timestamp() + " [Logger#info] init(): Finished initializing logger.\n")


def timestamp() -> str:
    """Return a Log timestamp.

    :return: Timestamp string.
    """
    # Thanks to https://stackoverflow.com/questions/3168096/getting-computers-utc-offset-in-python
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    return "{0}{1}".format(datetime.datetime.now().isoformat(), str(int(utc_offset / 3.6)))


class Logger:
    """Logger.

    Logs to STDOUT, and optionally to a file, and filters unwanted messages based on a log level setting.
    Each Logger instance can have its own namespace for which it tags messages.

    :ivar _namespace: The name of the subsystem this Logger instance is logging for.
    """

    def __init__(self, namespace) -> None:
        """Logger Initializer.

        :param namespace: The name of the subsystem this Logger instance is logging for.
        """
        self._namespace = namespace

    def debug(self, msg: str) -> None:
        """Write a debug level message to the console and/or the log file.

        :param msg: The message to log.
        """
        if self.__check_suppress("debug", msg):
            return
        if _LOGLEVEL in ["debug"]:
            if _STDOUT:
                print("{0} [{1}#debug] {2}".format(timestamp(), self._namespace, msg))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#debug] {2}\n".format(timestamp(), self._namespace, msg))

    def info(self, msg: str) -> None:
        """Write an info level message to the console and/or the log file.

        :param msg: The message to log.
        """
        if self.__check_suppress("info", msg):
            return
        if _LOGLEVEL in ["debug", "info"]:
            if _STDOUT:
                print("{0} [{1}#info] {2}".format(timestamp(), self._namespace, msg))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#info] {2}\n".format(timestamp(), self._namespace, msg))

    def warn(self, msg: str) -> None:
        """Write a warn level message to the console and/or the log file.

        :param msg: The message to log.
        """
        if self.__check_suppress("warn", msg):
            return
        if _LOGLEVEL in ["debug", "info", "warn"]:
            if _STDOUT:
                print("{0} [{1}#warn] {2}".format(timestamp(), self._namespace, msg))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#warn] {2}\n".format(timestamp(), self._namespace, msg))

    def error(self, msg: str) -> None:
        """Write an error level message to the console and/or the log file.

        :param msg: The message to log.
        """
        if self.__check_suppress("error", msg):
            return
        if _LOGLEVEL in ["debug", "info", "warn", "error"]:
            if _STDOUT:
                print("{0} [{1}#error] {2}".format(timestamp(), self._namespace, msg))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#error] {2}\n".format(timestamp(), self._namespace, msg))

    def critical(self, msg: str) -> None:
        """Write a critical level message to the console and/or the log file.

        All log levels include critical, so these messages cannot be disabled.
        Critical messages also cannot be suppressed.

        :param msg: The message to log.
        """
        print("{0} [{1}#critical] {2}".format(timestamp(), self._namespace, msg))
        if _LOGFILE:
            _LOGFILE.write("{0} [{1}#critical] {2}\n".format(timestamp(), self._namespace, msg))

        # Be nice to Windows users who ran the program by double-clicking. :)
        if _WAITONCRITICAL:
            input("Press Enter Key to Continue...")

    @staticmethod
    def write(msg: str) -> None:
        """Write an untagged message to the console and/or the log file, regardless of log level.

        :param msg: The message to log.
        """
        print(msg)
        if _LOGFILE:
            _LOGFILE.write("{0} {1}\n".format(timestamp(), msg))

    def __check_suppress(self, level: str, msg: str) -> bool:
        """Check whether a suppression rule suppresses this log message from appearing.

        :param level: The log level to check suppressions for.
        :param msg: The message to check suppressions for.
        """
        for S in _SUPPRESSIONS:
            if S[0] == level and S[1] == self._namespace:
                if S[2] in msg:
                    return True
        return False


