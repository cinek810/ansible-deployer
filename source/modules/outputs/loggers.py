"""Module for spawning customized loggers based on generic AnsibleDeployerLogger"""
from . import AnsibleDeployerLogger


class AppLogger(AnsibleDeployerLogger):
    """
    Create main application logger and add it's handlers
    memory handler exists until file handler is added in main function
    syslog handler will be added only if --syslog flag was set by operator
    """

    def __init__(self, options: dict):
        super().__init__("ansible-deployer_app_logger", options)
        self.add_syslog_handler()
        self.add_memory_handler()
        self.add_console_handler()
