"""Module for spawning customized loggers based on generic AnsibleDeployerLogger"""
from os.path import join as ospjoin
from typing import Tuple

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
        self.add_console_handler(self.console_formatter)


class RunLogger(AnsibleDeployerLogger):
    """
    Logger object created for each playitem from
    ansible_deployer.modules.runners.run.Runners.run_playitem()
    """

    def __init__(self, options: dict, workdir: str, playitem_name: str, inventory_name: str):
        name, log_path = self.set_runner_vars(workdir, playitem_name, inventory_name)
        super().__init__(name, options)
        self.add_syslog_handler()
        self.add_file_handler(log_path, self.raw_formatter)

        if options["raw_output"]:
            self.add_console_handler(self.raw_formatter)

    def set_runner_vars(self, workdir: str, playitem: str, inventory: str) -> Tuple[str, str]:
        """Set logger_name and log_path for current playitem in sequence"""
        playitem_fmt = playitem.replace(" ", "_")
        logger_name = f"ansible-deployer_runner_{playitem_fmt}_{inventory}_logger"
        log_path = ospjoin(workdir, f"rawlog_{playitem_fmt}_{inventory}.log")

        return logger_name, log_path
