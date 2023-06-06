######################
# BXEngine           #
# resourcemanager.py #
# Copyright 2021     #
# Sei Satzparad      #
######################

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

import json
import jsonschema
import os
import traceback
import sys

from typing import Optional

import pygame

from lib.logger import init, timestamp, Logger
from lib.util import normalize_path


class ResourceManager(object):
    """The Resource Manager

    Handles loading resources from disk, and validation of JSON files.

    :ivar resources: A dict of all currently loaded resources.
    :ivar config: This contains the engine's configuration variables.
    :ivar log: The Logger instance for this class.
    :ivar _loaded_schemas: A dict of all currently loaded JSON schemas.
    """
    def __init__(self):
        self.resources = {}
        self.config = None
        self.log = None
        self._loaded_schemas = {}

    def __contains__(self, item: str) -> bool:
        if item in self.resources:
            return True
        return False

    def __getitem__(self, item: str) -> Optional[dict]:
        if self.__contains__(item):
            return self.resources[item]
        else:
            return None

    def load_schema(self, schema: str) -> Optional[dict]:
        """Load a schema file for use in validating other JSON files.

        These are used when a schema is named in load_json().

        :param schema: The name of the schema type whose file to load. The filename will be "<schema>.json".
        :return: JSON object of the schema file if succeeded, otherwise the engine will exit.
        """
        # Return the schema if it is already loaded.
        if schema in self._loaded_schemas:
            return self._loaded_schemas[schema]

        # Begin loading a schema file.
        if self.log:
            self.log.info("load_schema(): Loading JSON Schema file: {0}".format(schema + ".json"))

        # Check the world directory for the schema first, followed by the common directory.
        if self.config and os.path.exists(self.config["world"] + "/schema/" + schema + ".json"):
            schema_fullpath = self.config["world"] + "/schema/" + schema + ".json"
        elif os.path.exists("common/schema/"+schema+".json"):
            schema_fullpath = "common/schema/"+schema+".json"
        else:
            if self.log:
                self.log.error("load_schema(): Could not locate schema file: {1}".format(timestamp(), schema + ".json"))
            return None

        # Attempt to load the schema.
        try:
            with open(schema_fullpath) as f:
                self._loaded_schemas[schema] = json.load(f)

        # Failed to load the schema.
        except (OSError, IOError):
            if self.log:
                self.log.error("load_schema(): Could not open schema file: {1}".format(timestamp(), schema+".json"))
            else:
                print("{0} [Resource#error] load_schema(): Could not open config schema file: {1}".format(
                    timestamp(), schema+".json"))
            print(traceback.format_exc(1))
            return None

        # Failed to decode the schema due to JSON error.
        except json.JSONDecodeError:
            if self.log:
                self.log.error("load_schema(): JSON error from schema file: {1}".format(timestamp(), schema+".json"))
            else:
                print("{0} [Resource#error] load_schema(): JSON error from config schema file: {1}".format(
                    timestamp(), schema+".json"))
            print(traceback.format_exc(1))
            return None

        # Return the loaded schema.
        return self._loaded_schemas[schema]

    def _load_initial_config(self, filename: str) -> dict:
        """Load the engine configuration file.

        :param filename: The filename of the configuration file to load.
        :return: Dictionary of configuration values if succeeded, otherwise the engine exits.
        """
        # Normalize the path to a Unix-style path for internal consistency.
        filename = normalize_path(filename)

        # If the config is already loaded, just return it. This shouldn't happen though.
        if self.config:
            return self.config

        # Attempt to load the JSON config file.
        try:
            with open(filename) as f:
                rsrc = json.load(f)

                # Load the schema needed to validate the config file, and perform validation.
                schema = self.load_schema("config")
                if not schema:
                    print("{0} [Resource#critical] _load_initial_config(): "
                          "Could not validate BXEngine config file: {1}".format(timestamp(), filename))
                    sys.exit(2)
                jsonschema.validate(rsrc, schema)

                # Finish loading the config.
                self.resources[filename] = rsrc
                self.config = rsrc

                # Initialize the Logger.
                init(self.config["log"]["level"], self.config["log"]["file"], self.config["log"]["stdout"],
                     self.config["log"]["suppress"],
                     self.config["log"]["wait_on_critical"])  # This is the init() from Logger.
                self.log = Logger("Resource")

                # Success.
                return self.config

        # Failed to open the config file.
        except (OSError, IOError):
            print("{0} [config#critical] _load_initial_config(): Could not open BXEngine config file: {1}".format(
                timestamp(), filename))
            print(traceback.format_exc(1))
            sys.exit(1)

        # Failed to decode the config file due to JSON error.
        except json.JSONDecodeError:
            print("{0} [config#critical] _load_initial_config(): JSON error from BXEngine config file: {1}".format(
                timestamp(), filename))
            print(traceback.format_exc(1))
            sys.exit(2)

        # The config file failed validation.
        except jsonschema.ValidationError:
            print("{0} [config#critical] _load_initial_config(): "
                  "JSON schema validation error from BXEngine config file: {1}".format(timestamp(), filename))
            print(traceback.format_exc(1))
            sys.exit(3)

    def load_json(self, filename: str, validate: str = None, rootdir: bool = False) -> Optional[dict]:
        """Load a JSON file.

        :param filename: The filename of the JSON file to load.
        :param validate: If set, the schema type to validate with. (Filename minus the ".json".)
        :param rootdir: Whether to search from the engine root directory instead of the world directory.
        :return: JSON object if succeeded, None if failed.
        """
        # Normalize the path to a Unix-style path for internal consistency.
        filename = normalize_path(filename)

        # If we're not searching from the root directory, prepend the world directory.
        if not rootdir:
            filename = os.path.join(self.config["world"], filename)

        # If the file is already loaded, just return it.
        if filename in self.resources:
            return self.resources[filename]

        # Attempt to load and optionally validate the JSON file.
        try:
            self.log.info("load_json(): Loading JSON file: {0}".format(filename))
            with open(filename) as f:
                rsrc = json.load(f)

                # Load the appropriate schema and attempt validation.
                if validate:
                    schema = self.load_schema(validate)
                    if not schema:
                        return None
                    jsonschema.validate(rsrc, schema)

                # Success.
                self.resources["filename"] = rsrc
                self.log.info("load_json(): Finished loading JSON file: {0}".format(filename))
                return self.resources["filename"]

        # Failed to open the JSON file.
        except (OSError, IOError):
            self.log.error("load_json(): Could not open JSON file: {0}".format(filename))
            print(traceback.format_exc(1))
            return None

        # Failed to decode the JSON file due to JSON error.
        except json.JSONDecodeError:
            self.log.error("load_json(): JSON error from BXEngine config file: {0}".format(filename))
            print(traceback.format_exc(1))
            return None

        # The JSON file failed validation.
        except jsonschema.ValidationError:
            self.log.error("load_json(): JSON schema validation error from file: {0}".format(filename))
            print(traceback.format_exc(1))
            return None

    def load_image(self, filename: str, scale: tuple = None, rootdir: bool = False) -> Optional[pygame.Surface]:
        """Load an image file.

        :param filename: The filename of the image to load.
        :param scale: A two-member tuple of the width and height to scale the image to.
        :param rootdir: Whether to search from the engine root directory instead of the world directory.
        :return: PyGame surface if succeeded, None if failed.
        """
        # Normalize the path to a Unix-style path for internal consistency.
        filename = normalize_path(filename)

        # If we're not searching from the root directory, prepend the world directory.
        if not rootdir:
            filename = os.path.join(self.config["world"], filename)

        # If the file is already loaded, just return it.
        if filename in self.resources:
            return self.resources[filename]

        # Attempt to load and optionally scale the image.
        try:
            # We are going to scale the image.
            if scale:
                rsrc = pygame.transform.scale(pygame.image.load(filename), scale)
                self.log.info("load_image(): Loading image file: {0}, at scale: {1}".format(filename, scale))

            # We are not going to scale the image.
            else:
                self.log.info("load_image(): Loading image file: {0}".format(filename))
                rsrc = pygame.image.load(filename)

            # Success.
            self.resources[filename] = rsrc
            self.log.info("load_image(): Finished loading image file: {0}".format(filename))
            return self.resources[filename]

        # We were unable to load the image.
        except:
            self.log.error("load_image(): Could not load image file: {0}".format(filename))
            return None

    def load_raw(self, filename: str, binary: bool = False, rootdir: bool = False) -> Optional[dict]:
        """Load any kind of file.

        :param filename: The filename of the file to load.
        :param binary: Whether to load the file in binary mode.
        :param rootdir: Whether to search from the engine root directory instead of the world directory.
        :return: Raw file data if succeeded, None if failed.
        """
        # Normalize the path to a Unix-style path for internal consistency.
        filename = normalize_path(filename)

        # If we're not searching from the root directory, prepend the world directory.
        if not rootdir:
            filename = os.path.join(self.config["world"], filename)

        # If the file is already loaded, just return it.
        if filename in self.resources:
            return self.resources[filename]

        # Attempt to load the file in binary or text mode.
        if binary:
            mode = 'rb'
        else:
            mode = 'rt'
        try:
            with open(filename, mode) as f:
                rsrc = f.read()

                # Success.
                self.resources["filename"] = rsrc
                self.log.info("load_raw(): Finished loading raw file: {0}".format(filename))
                return self.resources["filename"]

        # Failed to open the file.
        except (OSError, IOError):
            self.log.error("load_raw(): Could not open file: {0}".format(filename))
            print(traceback.format_exc(1))
            return None
