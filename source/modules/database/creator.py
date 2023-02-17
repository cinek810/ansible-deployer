"""Module for creating, initialization and connecting to database"""
import os
import sys
import sqlite3
import logging


class DbSetup:
    """Class handling creation and initialization of database"""

    def __init__(self, logger: logging, start_ts: str, conf: dict, options: dict):
        self.logger = logger
        self.start_ts = start_ts
        self.conf = conf
        self.options = options
        self.db_path = self.create_db_path()

    def create_db_path(self):
        """Create absolute path for database"""
        short_ts = self.start_ts.split("_")[0]
        db_name = self.options["infra"] + "_" + self.options["stage"] + ".db"
        return os.path.join(os.path.join(self.conf["global_paths"]["work_dir"], short_ts,
                                         self.conf["global_paths"]["database_subdir"], db_name))

    def create_db_dir(self):
        """Create directory containing databases"""
        db_dir = os.path.dirname(self.db_path)
        try:
            os.mkdir(db_dir)
            try:
                os.chmod(db_dir, int(self.conf["permissions"]["parent_workdir"], 8))
                self.logger.debug("Successfully created database directory: %s .", db_dir)
            except Exception as exc:
                self.logger.critical("Failed to change permissions of database directory: %s error"
                                     " was: %s", db_dir, exc)
                sys.exit(100)
        except FileExistsError:
            self.logger.debug("Database directory already exists: %s .", db_dir)
        except Exception as exc:
            self.logger.critical("Failed to create database directory: %s error was: %s.", db_dir,
                                 exc)
            sys.exit(100)

    def connect_to_db(self):
        """Create connector to sqlite database"""
        self.create_db_dir()
        try:
            connection = sqlite3.connect(self.db_path)
            self.logger.debug("Connection opened to database: %s .", self.db_path)
            db_perm_string = f"0o{''.join(str(oct(os.stat(self.db_path).st_mode))[-4:])}"
            if db_perm_string != self.conf["permissions"]["parent_workdir"]:
                self.change_db_permissions()
        except Exception as exc:
            self.logger.critical("Failed to connect to database: %s error was: %s.", self.db_path,
                                 exc)
            sys.exit(101)

        return connection, self.db_path

    def change_db_permissions(self):
        """Ensure correct permissions are set when database file is created"""
        try:
            os.chmod(self.db_path, int(self.conf["permissions"]["parent_workdir"], 8))
            self.logger.debug("Database %s permissions changed.", self.db_path)
        except Exception as exc:
            self.logger.critical("Failed to change permissions of database: %s error was: %s",
                                 self.db_path, exc)
            sys.exit(101)
