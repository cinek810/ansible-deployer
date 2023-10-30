"""Module for handling of logging and log files"""
from . import AnsibleDeployerLogger


class AppLogger(AnsibleDeployerLogger):

    def __init__(self, options: dict):
        super().__init__("ansible-deployer_app_logger", options)
        self.add_syslog_handler()
        self.add_memory_handler()
        self.add_console_handler()
