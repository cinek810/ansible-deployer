"""Main module for ansible-deploy"""

import os
import sys
import argparse
import datetime
import errno
import pkg_resources
from ansible_deployer.modules.configs.config import Config
from ansible_deployer.modules.locking.locking import Locking
from ansible_deployer.modules.outputs.logging import Loggers
from ansible_deployer.modules.validators.validate import Validators
from ansible_deployer.modules.runners.run import Runners
from ansible_deployer.modules.database.creator import DbSetup
from ansible_deployer.modules.database.writer import DbWriter
from ansible_deployer.modules import misc
from ansible_deployer.modules import globalvars

def parse_options(argv):
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument("subcommand", nargs='*', default=None, metavar="SUBCOMMAND",
                        help='Specify subcommand to execute. Available commands: '+ \
                        str(globalvars.SUBCOMMANDS))
    parser.add_argument("--infrastructure", "-i", nargs=1, default=[None], metavar="INFRASTRUCTURE",
                        help='Specify infrastructure for deploy.')
    parser.add_argument("--stage", "-s", nargs=1, default=[None], metavar="STAGE",
                        help='Specify stage type. Available types are: "testing" and "prod".')
    parser.add_argument("--commit", "-c", nargs=1, default=[None], metavar="COMMIT",
                        help='Provide commit ID.')
    parser.add_argument("--task", "-t", nargs=1, default=[None], metavar='TASK_NAME',
                        help='Provide task_name.')
    parser.add_argument("--dry", "-D", default=False, action='store_true', help='Perform dry run.')
    parser.add_argument("--keep-locked", "-k", default=False, action='store_true', help='Keep'
                        ' infrastructure locked after task execution.')
    parser.add_argument("--debug", "-d", default=False, action="store_true",
                        help='Print debug output.')
    parser.add_argument("--syslog", default=False, action="store_true", help='Log warnings and'
                        ' errors to syslog. --debug doesn\'t affect this option!')
    parser.add_argument("--limit", "-l", nargs=1, default=[None], metavar="[LIMIT]",
                        help='Limit task execution to specified host.')
    parser.add_argument("--conf-dir", "-C", nargs=1, default=[None], metavar="conf_dir",
                        help='Use non-default configuration directory, only allowed for \
                              non-binarized exec')
    parser.add_argument("--version", "-v", default=False, action="store_true", help='Display'
                            'app version and exit.')
    parser.add_argument("--raw-runner-output", default=False, action="store_true", help='Print'
                        ' original messages during runner execution instead of formatted ones.')
    parser.add_argument("--self-setup", nargs=1, default=[None], metavar="LOCAL_SETUP_PATH",
                        help='Setup repo outside of workdir in requested path. This option applies'
                        ' only to infrastructures with allow_user_checkout enabled in infra'
                        ' config!')
    parser.add_argument("--no-color", default=False, action="store_true", help='Disable coloring'
                        'of console messages.')

    arguments = parser.parse_args(argv)

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

    options = {}
    options["subcommand"] = arguments.subcommand[0].lower()
    Validators.verify_subcommand(options["subcommand"], arguments.no_color)
    Validators.verify_switches(arguments.subcommand, arguments.no_color)

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
    options["raw_output"] = arguments.raw_runner_output
    options["self_setup"] = os.path.abspath(arguments.self_setup[0]) if arguments.self_setup[0] \
                            else None
    options["conf_dir"] = os.path.abspath(arguments.conf_dir[0]) if arguments.conf_dir[0] else None
    options["no_color"] = arguments.no_color

    return options

def main():
    """ansible-deploy endpoint function"""
    start_ts_raw = datetime.datetime.now()
    start_ts = start_ts_raw.strftime("%Y%m%d_%H%M%S")

    if len(sys.argv) < 2:
        print(f"{globalvars.PRINT_FAIL}[CRITICAL]: Too few arguments{globalvars.PRINT_END}",
              file=sys.stderr)
        sys.exit(2)
    options = parse_options(sys.argv[1:])

    logger = Loggers(options)

    configuration = Config(logger.logger, options["conf_dir"])
    config = configuration.load_configuration()

    if options["subcommand"] in ("run", "verify"):
        workdir = misc.create_workdir(start_ts, configuration.conf, logger.logger)
        Loggers.set_logging_to_file(logger, workdir, start_ts, configuration.conf)
        logger.flush_memory_handler(True, options["syslog"])
    else:
        logger.flush_memory_handler(False, options["syslog"])

    validators = Validators(logger.logger)
    validators.validate_options(options)
    selected_items = validators.validate_option_values_against_config(config, options)

    if options["subcommand"] in ("run", "verify"):
        os.chdir(options["self_setup"] if options["self_setup"] else workdir)

    user_groups = misc.get_all_user_groups(logger.logger)

    if options["dry"]:
        logger.logger.info("Skipping execution because of --dry-run option")
        sys.exit(0)

    if options["subcommand"] == "show":
        misc.show_deployer(config, options)
    else:
        inv_file = misc.get_inventory_file(config, options)
        lockpath = os.path.join(os.path.join(configuration.conf["global_paths"]["work_dir"],
                                "locks") , inv_file.lstrip(f".{os.sep}").replace(os.sep, "_"))
        lock = Locking(logger.logger, options["keep_locked"], (options["infra"], options["stage"]),
                       configuration.conf)
        if options["subcommand"] in ("run", "verify"):
            if not validators.verify_task_permissions(selected_items, user_groups, config):
                logger.logger.critical("Task forbidden")
                sys.exit(errno.EPERM)
            runner = Runners(logger.logger, lock, workdir, start_ts_raw,
                             config["tasks"]["setup_hooks"])
            if not options["self_setup"]:
                runner.setup_ansible(selected_items["commit"])
            lock.lock_inventory(lockpath)
            db_connector, db_path = DbSetup.connect_to_db(DbSetup(logger.logger, start_ts,
                                                          configuration.conf, options))
            db_writer = DbWriter(logger.logger, db_connector, db_path)
            sequence_record_dict = runner.run_playitem(config, options, inv_file, lockpath,
                                                       db_writer)
            lock.unlock_inventory(lockpath)
            db_writer.finalize_db_write(sequence_record_dict, False)
        elif options["subcommand"] == "lock":
            lock.lock_inventory(lockpath)
        elif options["subcommand"] == "unlock":
            lock.unlock_inventory(lockpath)

    sys.exit(0)

if __name__ == "__main__":
    main()
