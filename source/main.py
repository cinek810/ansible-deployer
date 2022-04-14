"""Main module for ansible-deploy"""

import os
import sys
import argparse
import datetime
import errno
from ansible_deployer.modules.globalvars import SUBCOMMANDS
from ansible_deployer.modules.configs.config import Config
from ansible_deployer.modules.locking.locking import Locking
from ansible_deployer.modules.outputs.logging import Loggers
from ansible_deployer.modules.validators.validate import Validators
from ansible_deployer.modules.runners.run import Runners
from ansible_deployer.modules import misc


def parse_options(argv):
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument("subcommand", nargs='*', default=None, metavar="SUBCOMMAND",
                        help='Specify subcommand to execute. Available commands: '+str(SUBCOMMANDS))
    parser.add_argument("--infrastructure", "-i", nargs=1, default=[None], metavar="INFRASTRUCTURE",
                        help='Specify infrastructure for deploy.')
    parser.add_argument("--stage", "-s", nargs=1, default=[None], metavar="STAGE",
                        help='Specify stage type. Available types are: "testing" and "prod".')
    parser.add_argument("--commit", "-c", nargs=1, default=[None], metavar="COMMIT",
                        help='Provide commit ID.')
    parser.add_argument("--task", "-t", nargs=1, default=[None], metavar='TASK_NAME',
                        help='Provide task_name.')
    parser.add_argument("--dry", "-C", default=False, action='store_true', help='Perform dry run.')
    parser.add_argument("--keep-locked", "-k", default=False, action='store_true', help='Keep'
                        ' infrastructure locked after task execution.')
    parser.add_argument("--debug", "-d", default=False, action="store_true",
                        help='Print debug output.')
    parser.add_argument("--syslog", "-v", default=False, action="store_true", help='Log warnings '
                        'and errors to syslog. --debug doesn\'t affect this option!')
    parser.add_argument("--limit", "-l", nargs=1, default=[None], metavar="[LIMIT]",
                        help='Limit task execution to specified host.')
    parser.add_argument("--conf-dir", nargs=1, default=[None], metavar="conf_dir",
                        help='Use non-default configuration directory, only allowed for \
                              non-binarized exec')

    arguments = parser.parse_args(argv)

    if not arguments.subcommand:
        sub_string = ", ".join(SUBCOMMANDS).strip(", ")
        print(f"[CRITICAL]: First positional argument (subcommand) is required! Available commands"
              f" are: {sub_string}.")
        sys.exit(57)

    options = {}
    options["subcommand"] = arguments.subcommand[0].lower()
    Validators.verify_subcommand(options["subcommand"])
    Validators.verify_switches(arguments.subcommand)

    options["switches"] = arguments.subcommand[1:]
    options["infra"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]
    options["dry"] = arguments.dry
    options["keep_locked"] = arguments.keep_locked
    options["debug"] = arguments.debug
    options["syslog"] = arguments.syslog
    options["limit"] = arguments.limit[0]
    if arguments.conf_dir[0]:
        options["conf_dir"] = os.path.abspath(arguments.conf_dir[0])
    else:
        options["conf_dir"] = None

    return options

def main():
    """ansible-deploy endpoint function"""
    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if len(sys.argv) < 2:
        print("[CRITICAL]: Too few arguments", file=sys.stderr)
        sys.exit(2)
    options = parse_options(sys.argv[1:])

    logger = Loggers(options)

    configuration = Config(logger.logger, options["conf_dir"])
    conf = configuration.conf
    config = configuration.load_configuration()

    if options["subcommand"] in ("run", "verify"):
        workdir = misc.create_workdir(start_ts, conf, logger.logger)
        Loggers.set_logging_to_file(logger, workdir, start_ts, conf)

    validators = Validators(logger.logger)
    validators.validate_options(options)
    selected_items = validators.validate_option_values_against_config(config, options)

    user_groups = misc.get_all_user_groups(logger.logger)

    if options["dry"]:
        logger.logger.info("Skipping execution because of --dry-run option")
        sys.exit(0)

    if options["subcommand"] == "list":
        misc.list_tasks(config, options)
    elif options["subcommand"] == "show":
        misc.show_deployer(config, options)
    else:
        lockdir = os.path.join(conf["global_paths"]["work_dir"], "locks")
        inv_file = misc.get_inventory_file(config, options)
        lockpath = os.path.join(lockdir, inv_file.lstrip(f".{os.sep}").replace(os.sep, "_"))
        lock = Locking(logger.logger, options["keep_locked"], (options["infra"], options["stage"]))
        if options["subcommand"] in ("run", "verify"):
            if not validators.verify_task_permissions(selected_items, user_groups, config):
                logger.logger.critical("Task forbidden")
                sys.exit(errno.EPERM)
            runner = Runners(logger.logger, lock)
            runner.setup_ansible(config["tasks"]["setup_hooks"], options["commit"], workdir)
            lock.lock_inventory(lockdir, lockpath)
            runner.run_playitem(config, options, inv_file, lockpath)
            lock.unlock_inventory(lockpath)
        elif options["subcommand"] == "lock":
            lock.lock_inventory(lockdir, lockpath)
        elif options["subcommand"] == "unlock":
            lock.unlock_inventory(lockpath)

    sys.exit(0)

if __name__ == "__main__":
    main()
