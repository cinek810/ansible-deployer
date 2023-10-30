"""Module designed to handle all arguments"""
from argparse import ArgumentParser, Namespace
from typing import Optional, Tuple
import os
import sys
import pkg_resources

from ansible_deployer.modules.validators.validate import Validators
from ansible_deployer.modules import globalvars


class CliInput:
    """Class designed to parse and validate command line arguments"""

    @staticmethod
    def create_parser() -> ArgumentParser:
        """Generic function to parse options for all commands"""
        parser = ArgumentParser(add_help=True)

        parser.add_argument("subcommand", nargs='*', default=None, metavar="SUBCOMMAND",
                            help='Specify subcommand to execute. Available commands: ' +
                                 str(globalvars.SUBCOMMANDS))
        parser.add_argument("--check-mode", "-C", action="store_true",
                            help='Enable --check-mode/-C when using default runner'
                                 ' (ansible-playbook).')
        parser.add_argument("--commit", "-c", nargs=1, default=[None], metavar="COMMIT",
                            help='Provide commit ID.')
        parser.add_argument("--conf-dir", nargs=1, default=[None], metavar="conf_dir",
                            help='Use non-default configuration directory, only allowed for'
                                 ' non-binarized exec')
        parser.add_argument("--conf-validation", default=False, action='store_true',
                            help='Execute configuration files validation and exit program.')
        parser.add_argument("--debug", "-d", default=False, action="store_true",
                            help='Print debug output. This option does not affect runner output'
                                 ' (use --raw-runner-output for that).')
        parser.add_argument("--dry-mode", "-D", action="store_true",
                            help='Execute default runner (ansible-playbook) with'
                                 ' "ansible_deployer_dry_mode" tag, triggering only required'
                                 ' variable validation in pre_tasks. This tag is not predefined!')
        parser.add_argument("--infrastructure", "-i", nargs=1, default=[None],
                            metavar="INFRASTRUCTURE",
                            help='Specify infrastructure for deploy.')
        parser.add_argument("--inventory", "-I", nargs=1, default=[None], metavar="INVENTORY",
                            help='Specify inventory, only allowed if not set in configuration')
        parser.add_argument("--keep-locked", "-k", default=False, action='store_true',
                            help='Keep infrastructure locked after task execution.')
        parser.add_argument("--limit", "-l", nargs=1, default=[None], metavar="[LIMIT]",
                            help='Limit task execution to specified host.')
        parser.add_argument("--no-color", default=False, action="store_true",
                            help='Disable coloring of console messages.')
        parser.add_argument("--no-lock", default=False, action="store_true",
                            help='Do not lock the infrastructure')
        parser.add_argument("--raw-runner-output", default=False, action="store_true",
                            help='Print original messages in real time during runner execution.')
        parser.add_argument("--runner-plugins", nargs=1, default=[None], metavar='TASK_NAME',
                            help='Provide comma-separated list of plugins to enable.')
        parser.add_argument("--runner-raw-file", default=False, action="store_true",
                            help='Print original messages to main log file.')
        parser.add_argument("--runner-stdout", nargs=1, default=[None], metavar='STDOUT_PLUGIN',
                            help=
                            'Provide name of runner stdout callback plugin you would like to use.')
        parser.add_argument("--self-setup", nargs=1, default=[None], metavar="LOCAL_SETUP_PATH",
                            help='Setup repo outside of workdir in requested path. This option'
                                 ' applies only to infrastructures with allow_user_checkout enabled'
                                 ' in infra config!')
        parser.add_argument("--stage", "-s", nargs=1, default=[None], metavar="STAGE",
                            help='Specify stage type. Available types are: "testing" and "prod".')
        parser.add_argument("--syslog", default=False, action="store_true", help='Log warnings and'
                            ' errors to syslog. --debug doesn\'t affect this option!')
        parser.add_argument("--task", "-t", nargs=1, default=[None], metavar='TASK_NAME',
                            help='Provide task_name.')
        parser.add_argument("--version", "-v", default=False, action="store_true",
                            help='Display app version and exit.')

        return parser

    def parse_arguments(self) -> dict:
        """
        Generic function that returns options dict after triggering command line arguments parsing
        and validation.
        """
        return self.validate_arguments(self.create_parser().parse_args())

    def validate_arguments(self, arguments: Namespace) -> dict:
        """
        Generic function that returns options dict after triggering command line arguments
        validation
        """
        return self.validate_rest_arguments(arguments, *self.validate_init_arguments(arguments))

    @staticmethod
    def validate_init_arguments(arguments: Namespace) -> Tuple[str, str]:
        """Validate selected parsed arguments for specific handling"""
        if arguments.version:
            version = pkg_resources.require("ansible_deployer")[0].version
            print(f"ansible-deployer version: {version}")
            sys.exit(0)

        if arguments.no_color:
            PRINT_FAIL = PRINT_END = ""
        else:
            PRINT_FAIL = globalvars.PRINT_FAIL
            PRINT_END = globalvars.PRINT_END

        if not arguments.subcommand:
            sub_string = ", ".join(globalvars.SUBCOMMANDS).strip(", ")
            print(f"{PRINT_FAIL}[CRITICAL]: First positional argument (subcommand) is required!"
                  f" Available commands are: {sub_string}.{PRINT_END}")
            sys.exit(57)

        return PRINT_END, PRINT_FAIL

    def validate_rest_arguments(self, arguments: Namespace, print_end: str, print_fail: str
                                ) -> dict:
        """Validate remaining parsed arguments and collect them into dictionary"""
        options = {}
        options["subcommand"] = arguments.subcommand[0].lower()
        Validators.verify_subcommand(options["subcommand"], arguments.no_color)
        Validators.verify_switches(arguments.subcommand, arguments.no_color)

        options["switches"] = arguments.subcommand[1:]
        options["check_mode"] = arguments.check_mode
        options["commit"] = arguments.commit[0]
        options["conf_dir"] = os.path.abspath(arguments.conf_dir[0]) if arguments.conf_dir[0]\
            else None
        options["conf_val"] = arguments.conf_validation
        options["debug"] = arguments.debug
        options["dry_mode"] = arguments.dry_mode
        options["infra"] = arguments.infrastructure[0]
        options["inventory"] = arguments.inventory[0]
        options["keep_locked"] = arguments.keep_locked
        options["limit"] = arguments.limit[0]
        options["lock"] = not arguments.no_lock
        options["no_color"] = arguments.no_color
        options["raw_output"] = arguments.raw_runner_output
        options["runner_plugins"] = self.validate_ansible_callback(
            arguments.runner_plugins[0], print_fail, print_end)
        options["runner_raw_file"] = arguments.runner_raw_file
        options["runner_stdout"] = self.validate_ansible_stdout_callback(arguments.runner_stdout,
                                                                         print_fail, print_end)
        options["self_setup"] = os.path.abspath(arguments.self_setup[0]) if arguments.self_setup[0]\
            else None
        options["stage"] = arguments.stage[0]
        options["syslog"] = arguments.syslog
        options["task"] = arguments.task[0]

        return options

    @staticmethod
    def validate_ansible_stdout_callback(stdout_plugin: str, print_fail: str, print_end: str
                                         ) -> Optional[str]:
        """Validate whether plugin (specified via --runner-stdout option) is supported"""
        try:
            lplugin = stdout_plugin[0].lower()
            if lplugin in globalvars.SUPPORTED_STDOUT_CALLBACK_PLUGINS:
                return lplugin

            print(f"{print_fail}[CRITICAL]: Unsupported runner stdout callback plugin!"
                  f"{print_end}")
            sys.exit(57)
        except AttributeError:
            return None

    @staticmethod
    def validate_ansible_callback(stdout_plugin: str, print_fail: str, print_end: str
                                  ) -> Optional[list]:
        """Validate whether plugin (specified via --runner-plugin option) is supported"""
        if stdout_plugin:
            try:
                plugins = stdout_plugin.split(",")
                if all(plugin in globalvars.SUPPORTED_CALLBACK_PLUGINS for plugin in plugins):
                    return plugins

                print(f"{print_fail}[CRITICAL]: Unsupported runner callback plugin!"
                      f"{print_end}")
                sys.exit(57)
            except Exception:
                print(f"{print_fail}[CRITICAL]: Invalid format of runner callback plugin!"
                      f"{print_end}")
                sys.exit(57)
        else:
            return []
