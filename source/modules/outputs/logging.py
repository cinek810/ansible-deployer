"""Module for handling of logging and log files"""

import os
import logging
from logging import handlers as log_han


class Loggers:
    """Class handling creating logger and logging handlers"""

    def __init__(self, options: dict):
        self.logger = self.set_logging(options)

    @staticmethod
    def set_logging(options: dict):
        """Function to create logging objects"""
        logger = logging.getLogger("ansible-deployer_log")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        console_formatter = "\n%(asctime)s [%(levelname)s]: %(message)s\n"

        if options["syslog"]:
            rsys_handler = log_han.SysLogHandler(address="/dev/log")
            rsys_handler.setFormatter(formatter)
            rsys_handler.setLevel(logging.WARNING)
            logger.addHandler(rsys_handler)

        memory_handler = log_han.MemoryHandler(15, flushLevel=logging.DEBUG, flushOnClose=False)
        memory_handler.setFormatter(formatter)
        memory_handler.setLevel(logging.DEBUG)
        logger.addHandler(memory_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(console_formatter) if options["no_color"] \
                                     else CustomFormatter(console_formatter))
        console_handler.setLevel(logging.DEBUG if options["debug"] else logging.INFO)
        logger.addHandler(console_handler)

        return logger

    def set_logging_to_file(self, log_dir: str, timestamp: str, conf: dict):
        """Function adding file handler to existing logger"""
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir,
                                conf["file_naming"]["log_file_name_frmt"].format(timestamp))
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)


class CustomFormatter(logging.Formatter):
    """Class adding colours to console logger"""

    def __init__(self, formatter):
        super().__init__()
        grey = "\x1b[0;38m"
        light_green = "\x1b[1;32m"
        yellow = "\x1b[0;33m"
        red = "\x1b[0;31m"
        light_red = "\x1b[1;31m"
        reset = "\x1b[0m"

        self.FORMATS = {
            logging.DEBUG: light_green + formatter + reset,
            logging.INFO: grey + formatter + reset,
            logging.WARNING: yellow + formatter + reset,
            logging.ERROR: red + formatter + reset,
            logging.CRITICAL: light_red + formatter + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
