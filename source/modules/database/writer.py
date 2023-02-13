"""Module for writing data to existing database"""
import sys
import os
import datetime
import sqlite3
import yaml
from ansible_deployer.modules.database.schema import SCHEMAS


class DbWriter:
    """Class handling writing records to database"""

    def __init__(self, logger, connector, db_path: str):
        self.logger = logger
        self.connector = connector
        self.db_path = db_path
        self.cursor = self.connector.cursor()
        self.create_tables()

    def create_tables(self):
        """Create database tables for all keys in schema"""
        for key in SCHEMAS:
            self.create_table(key)

    def create_table(self, table_name: str):
        """Create single database table"""
        base_format = str(len(SCHEMAS[table_name]) * "'{}', ").strip(", ")
        table_string = f'''CREATE TABLE {table_name} ({base_format})'''
        try:
            self.cursor.execute(table_string.format(*SCHEMAS[table_name].keys()))
            self.logger.debug("Created table %s in database %s .", table_name, self.db_path)
        except sqlite3.OperationalError:
            self.logger.debug("Table %s already exists in database %s .", table_name, self.db_path)
        except Exception as exc:
            self.logger.critical("Failed table %s creation in database %s, error was %s",
                                 table_name, self.db_path, exc)
            sys.exit(104)

    def parse_yaml_output(self, stream: list, sequence_id: str):
        """Parse ansible output in yaml format"""
        record_dict = {}
        try:
            for task in stream:
                splitted = task.split("\n")
                for no, line in enumerate(splitted):
                    if "TASK" in line:
                        task_name = line.split("[")[1].split("]")[0]
                        record_dict[task_name] = {}
                    if "changed" in line:
                        host_name = line.split("[")[1].split("]")[0]
                        yaml_string = "\n".join(splitted[no+1:no+11])
                        record_dict[task_name][host_name] = dict(SCHEMAS["play_item_tasks"])
                        record_dict[task_name][host_name]["task_name"] = task_name
                        record_dict[task_name][host_name]["sequence_id"] = sequence_id
                        record_dict[task_name][host_name]["hostname"] = host_name
                        for key, value in yaml.safe_load(yaml_string).items():
                            for schema_key in record_dict[task_name][host_name].keys():
                                if key == schema_key:
                                    record_dict[task_name][host_name][schema_key] = value
            return record_dict

        except Exception as exc:
            self.logger.critical("Failed parsing output stream to yaml, error was %s", exc)
            sys.exit(102)

    def write_records(self, record_dict: dict):
        """Write multiple records to "play_item_tasks" table"""
        host_list = []
        for hosts in record_dict.values():
            for host, records in hosts.items():
                host_list.append(host)
                record_list = []
                for param in records.values():
                    record_list.append(param)
                self.write_record("play_item_tasks", record_list)

        return host_list

    def write_record(self, table_name, record):
        """Write single record to any table"""
        base_format = str(len(record) * "'{}', ").strip(", ")
        insert_string = f"INSERT INTO {table_name} VALUES ({base_format})"
        try:
            self.cursor.execute(insert_string.format(*record))
        except Exception as exc:
            self.logger.critical("Failed writing record to database %s, error was %s",
                                 self.db_path, exc)
            sys.exit(105)

    def commit_changes(self):
        """Commit changes to sqlite database"""
        try:
            self.connector.commit()
            self.logger.debug("Changes saved to database %s .", self.db_path)
        except Exception as exc:
            self.logger.critical("Failed saving changes to database %s, error was %s",
                                 self.db_path, exc)
            sys.exit(103)

    def start_sequence_dict(self, hosts: list, setup_hooks: list, options: dict, start_ts_raw: str,
                            sequence_id: str):
        """Create dictionary with constant values for "sequences" table records"""
        sequence_dict = {}
        hosts = list(set(hosts))
        for host in hosts:
            sequence_dict[host] = self.fill_sequence_dict(sequence_id, host, setup_hooks, options,
                                                          start_ts_raw)

        return sequence_dict

    @staticmethod
    def fill_sequence_dict(sequence_id: str, host: str, setup_hooks: list, options: dict,
                           start_ts_raw: str):
        """Assign values to keys (columns) for sequence record dictionary"""
        sub_sequence_dict = dict(SCHEMAS["sequences"])
        sub_sequence_dict["sequence_id"] = sequence_id
        sub_sequence_dict["hostname"] = host
        sub_sequence_dict["user_id"] = os.getuid()
        hook_names = []
        for hook in setup_hooks:
            hook_names.append(hook["name"])
        sub_sequence_dict["hooks"] = ", ".join(hook_names)
        sub_sequence_dict["task"] = options["task"]
        sub_sequence_dict["start"] = start_ts_raw
        sub_sequence_dict["keep_locked_on"] = bool(options["keep_locked"])
        sub_sequence_dict["self_setup_on"] = bool(options["self_setup"])
        sub_sequence_dict["conf_dir_on"] = bool(options["conf_dir"])

        return sub_sequence_dict

    def finalize_db_write(self, sequence_dict: dict, host_locked: bool):
        """Add final values to sequence record dictionary, commit changes and close database
        connection"""
        end_ts = datetime.datetime.now()
        for params in sequence_dict.values():
            record_list = []
            params["end"] = end_ts
            params["host_locked"] = host_locked
            for params2 in params.values():
                record_list.append(params2)
            self.write_record("sequences", record_list)
        self.commit_changes()
        self.connector.close()
