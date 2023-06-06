######################
# BXEngine           #
# databasemanager.py #
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
import os
import sys
import ubjson
from typing import Any, Optional

from lib.logger import Logger


class DatabaseManager:
    """The Database Manager

    Stores and retrieves named objects through a Universal Binary JSON file.
    Any object type supported by JSON may be stored.

    :ivar config: This contains the engine's configuration variables.
    :ivar log: The Logger instance for this class.
    :ivar filename: The filename of the initial database to open.
    :ivar __change: Whether are changes to the database that haven't been written to disk yet.
    :ivar __database: The JSON contents of the currently open database.
    """

    def __init__(self, config):
        """DatabaseManager Class Initializer

        :param config: This contains the engine's configuration variables.
        """
        self.config = config
        self.log = Logger("DatabaseManager")

        self.filename = os.path.join(self.config["database"])

        # Has the database changed in memory?
        self.__changed = False

        # Make sure the database directory is accessible.
        if not self.__test_db_dir():
            sys.exit(4)  # Fail.

        self.__database = self.__load()

        # Make sure the database is accessible.
        if self.__database is None:
            self.log.critical("__init__(): Cannot open initial database: {0}".format(self.filename))
            sys.exit(5)  # Fail.

        self.log.info("__init__(): Opened initial database: {0}".format(self.filename))

    def __contains__(self, item: str) -> bool:
        if item in self.__database:
            return True
        return False

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __setitem__(self, item: str, obj: Any) -> None:
        self.put(item, obj)

    def __delitem__(self, item: str) -> None:
        self.remove(item)

    def open(self, filename: str) -> bool:
        """Opens a new database and closes the current one.

        If opening the new database fails, the old one stays loaded.

        :param filename: The filename of the database to load, relative to the database root.
        :return: True if succeeded, False if failed.
        """
        self.flush()  # Write the current database to disk first.

        old_filename = self.filename  # Keep track of the old filename.
        self.filename = filename  # Set the new filename.

        if not self.__test_db_open():  # Test and possibly create the new file.
            self.filename = old_filename  # We failed, revert.
            self.log.error("open(): Cannot open database: {0}".format(self.filename))
            return False

        new_database = self.__load()  # Load the new database into a temporary variable.

        if new_database is None:  # Did it not load correctly?
            self.filename = old_filename  # We failed, revert.
            self.log.error("open(): Cannot open database: {0}".format(self.filename))
            return False

        self.__database = new_database  # Replace the old database in memory with the new one.
        self.log.info("open(): Opened new database: {0}".format(self.filename))
        return True  # Success

    def get(self, key: str) -> Any:
        """Retrieve an object from the database by its key .

        :param key: The key whose object to retrieve.
        :return: Python object if succeeded, None if failed.
        """
        # Get the key.
        if key in self.__database:
            self.log.debug("get(): Get object: \"{0}\"".format(key))
            return self.__database[key]

        # Failed to get the key.
        else:
            self.log.error("get(): No such key: \"{0}\"".format(key))
            return None

    def put(self, key: str, obj: Any) -> bool:
        """Create or update a key with a new object.

        :var key: The key to create or update.
        :var obj: The object to store.
        :return: True if succeeded, False if failed.
        """
        # Is it serializable?
        try:
            ret = json.dumps(obj)
        except TypeError:
            self.log.error("put(): Bad object type for key: \"{0}\"".format(key))
            return False

        self.__database[key] = obj
        self.__changed = True
        self.log.debug("put(): Put object: \"{0}\"".format(key))
        return True

    def remove(self, key: str) -> bool:
        """Removes a key and its object from the database.

        :param key: The key to remove.
        :return: True if succeeded, False if failed.
        """
        # Remove the key.
        if key in self.__database:
            del self.__database[key]
            self.log.debug("remove(): Remove object: \"{0}\"".format(key))
            self.__changed = True
            return True
        else:
            self.log.error("remove(): No such key: \"{0}\"".format(key))
            return False

    def flush(self) -> None:
        """Force the database to write to disk now.
        """
        self.__changed = True
        self._update()
        self.log.debug("flush(): Flushed database to disk: {0}".format(self.filename))

    def __test_db_dir(self) -> bool:
        """Test if we can create or open the database directory.

        :return: True if succeeded, False if failed.
        """
        db_dir_path = os.path.dirname(self.config["database"])
        if db_dir_path == '':
            db_dir_path = '.'
        try:
            # Create db directory
            if not os.path.isdir(db_dir_path):
                self.log.info("Creating database directory: {0}".format(db_dir_path))
                os.mkdir(db_dir_path)
        except:
            self.log.critical("__test_db_dir(): Cannot create database directory: {0}".format(db_dir_path))
            return False

        try:
            # Try opening the directory
            os.listdir(db_dir_path)
        except:
            self.log.critical("__test_db_dir(): Cannot open database directory: {0}".format(db_dir_path))
            return False

        return True

    def __test_db_open(self) -> bool:
        """Test if we can create or open the database file.

        :return: True if succeeded, False if failed.
        """
        try:
            with open(self.filename, "ab+") as test:
                return True
        except:
            return False

    def __load(self) -> Optional[dict]:
        """Load the database file from disk.

        :return: Object if succeeded, False if failed.
        """
        if not self.__test_db_open():
            return None

        try:
            with open(self.filename, 'rb') as dbfile:
                database_contents = dbfile.read()
                if len(database_contents):
                    return ubjson.loadb(database_contents)
                else:
                    return {}
        except:
            return None

    def _update(self) -> None:
        """Tick callback.

        If there have been any changes to the database in memory, write them to disk.
        """
        if self.__changed:
            try:
                with open(self.filename, 'wb') as dbfile:
                    dbfile.write(ubjson.dumpb(self.__database))
            except:
                self.log.critical("_update(): Suddenly cannot write database to disk: {0}".format(self.filename))
                sys.exit(6)
            self.__changed = False

