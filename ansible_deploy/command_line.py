"""Main module for ansible-deploy"""

import sys
import os
import argparse
import logging
import datetime
import subprocess
import pwd
#TODO: Add an option to explicitly enable syslog logging
#from logging import handlers as log_han

import yaml
from cerberus import Validator


CONF = "/etc/ansible-deploy/ansible-deploy.yaml"
LOG_NAME_FRMT = "ansible-deploy_execution_{}.log"


def get_sub_command(command):
    """Function to check the first arguments (argv[1..]) looking for a subcommand"""
    if command == "run":
        subcommand = "run"
    elif command == "lock":
        subcommand = "lock"
    elif command == "unlock":
        subcommand = "unlock"
    elif command == "list":
        subcommand = "list"
    else:
        logger.error("Unknown subcommand :%s", (command))
        sys.exit("55")
    logger.debug("Returning subcommand: %s", subcommand)
    return subcommand

def set_logging(log_dir: str, name: str, timestamp: str):
    """Function to create logging objects"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, name.format(timestamp))

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    console_formatter = logging.Formatter("\n%(asctime)s [%(levelname)s]: %(message)s\n")

#   TODO: Add an option to explicitly enable syslog logging
#    rsys_handler = log_han.SysLogHandler(address="/dev/log")
#    rsys_handler.setFormatter(formatter)
#    rsys_handler.setLevel(logging.ERROR)
#    logger.addHandler(rsys_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


def parse_options(argv):
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--infrastructure", "-i", nargs=1, default=[None], metavar="INFRASTRUCTURE",
                        help='Specify infrastructure for deploy.')
    parser.add_argument("--stage", "-s", nargs=1, default=[None], metavar="STAGE",
                        help='Specify stage type. Available types are: "testing" and "production".')
    parser.add_argument("--commit", "-c", nargs=1, default=[None], metavar="COMMIT", help='Provide '
                        'commit ID.')
    parser.add_argument("--task", "-t", nargs=1, default=[None], metavar='"TASK NAME"',
                        help='Provide task name in "".')
    parser.add_argument("--dry", default=False, action='store_true')

    arguments = parser.parse_args(argv)

    options = {}
    options["infra"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]
    options["dry"] = arguments.dry

    return options

def create_workdir(timestamp: str, base_dir: str):
    """
    Function to create working directory on file system, we expect it to change
    the cwd to newly created workdir at the end.
    """
    logger.debug("Entering create_workdir")
    short_ts = timestamp.split("_")[0]
    date_dir = os.path.join(base_dir, short_ts)

    #
    #TODO: Add locking of the directory

    if short_ts not in os.listdir(base_dir):
        seq_path = os.path.join(date_dir, f"{conf['file_naming']['sequence_prefix']}0000")
    else:
        sequence_list = os.listdir(date_dir)
        sequence_list.sort()
        new_sequence = int(sequence_list[-1].split(conf['file_naming']['sequence_prefix'])[1]) + 1
        seq_path = os.path.join(date_dir, f"{conf['file_naming']['sequence_prefix']}"
                                          f"{new_sequence:04d}")

    #TODO: Add error handling
    os.makedirs(seq_path)
    os.chdir(seq_path)
    logger.info("Successfully created workdir: %s", seq_path)
    return seq_path

def validate_options(options, subcommand):
    """Function checking if the options set are allowed in this subcommand"""
    logger.debug("validate_options running for subcommand: %s", (subcommand))
    required = []
    notsupported = []
    if subcommand == "run":
        required = ["task", "infra", "stage"]
    elif subcommand in ("lock", "unlock"):
        required = ["infra", "stage"]
        notsupported = ["task", "commit"]
    elif subcommand == "list":
        notsupported = ["commit"]

    failed = False
    for req in required:
        if options[req] is None:
            logger.error("%s is required for %s", req, subcommand)
            failed = True

    for notsup in notsupported:
        if options[notsup] is not None:
            logger.error("%s is not supported by %s", notsup, subcommand)
            failed = True

    if failed:
        logger.error("Failed to validate options")
        sys.exit(55)
    else:
        return required

def load_configuration_file(config_file):
    """Function responsible for single file loading and validation"""
    #TODO: Add verification of owner/group/persmissions
    logger.debug("Loading :%s", config_file)

    with open(os.path.join(conf["global_paths"]["config_dir"], config_file), "r", encoding="utf8") \
            as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(51)

    with open(os.path.join(conf["global_paths"]["config_dir"], "schema", config_file), "r",
              encoding="utf8") as schema_stream:
        try:
            schema = yaml.safe_load(schema_stream)
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(52)
    validator = Validator(schema)
    if not validator.validate(config, schema):
        logger.error(validator.errors)
        sys.exit(53)
    logger.debug("Loaded:\n%s", str(config))
    return config

def load_configuration():
    """Function responsible for reading configuration files and running a schema validator against
    it
    """
    logger.debug("load_configuration called")
    #TODO: validate files/directories permissions - should be own end editable only by special user

    infra = load_configuration_file("infra.yaml")
    tasks = load_configuration_file("tasks.yaml")

    config = {}
    config["infra"] = infra["infrastructures"]
    config["tasks"] = tasks

    return config

def validate_option_by_dict_with_name(optval, conf_dict):
    """
    Validate if given dictionary contains element with name equal to optval
    """
    if optval:
        for elem in conf_dict:
            if elem["name"] == optval:
                break
        else:
            logger.error("%s not found in configuration file.", optval)
            sys.exit(54)

def validate_user_infra_stage():
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations"""

def validate_user_task():
    """Function checking if user has rights to execute the task
    Rquired for: run"""


def validate_option_values_against_config(config: dict, options: dict, required_opts: list):
    """
    Function responsible for checking if option values match configuration
    """
    for option in options.keys():
        if option in required_opts:
            validate_option_values_with_config(config, options, option)


def validate_option_values_with_config(config: dict, options: dict, option: str):
    """
    Function responsible for checking if option values match configuration
    """

    if option == "infra":
        validate_option_by_dict_with_name(options["infra"], config["infra"])
    elif option == "task":
        validate_option_by_dict_with_name(options["task"], config["tasks"]["tasks"])
    elif option == "stage":
        for item in config["infra"]:
            if item["name"] == options["infra"]:
                index = config["infra"].index(item)
        validate_option_by_dict_with_name(options["stage"], config["infra"][index]["stages"])
    #TODO: validate if user is allowed to use --commit
    #TODO: validate if user is allowed to execute the task on infra/stag pair
    #(validate_user_infra_stage(), validate_usr_task())


def lock_inventory(lockdir: str, lockpath: str):
    """
    Function responsible for locking inventory file.
    The goal is to prevent two parallel ansible-deploy's running on the same inventory
    This needs to be done by the use of additional directory under PARNT_WORKDIR,, for instance:
    PARENT_WORKDIR/locks.
    We shouldn't check if file exists, but rather attempt to open it for writing, until we're
    done every other process should be rejected this access.
    The file should match inventory file name.
    """

    logger.debug("Started lock_inventory for lockdir: %s and lockpath %s.", lockdir, lockpath)
    os.makedirs(lockdir, exist_ok=True)

    try:
        with open(lockpath, "x", encoding="utf8") as fh:
            fh.write(str(os.getpid()))
            fh.write(str("\n"))
            fh.write(str(pwd.getpwuid(os.getuid()).pw_name))
        logger.info("Infra locked.")
    except FileExistsError:
        with open(lockpath, "r", encoding="utf8") as fh:
            proc_pid, proc_user = fh.readlines()
        logger.error("Another process (PID: %s) started by user %s is using this infrastructure, "
                     "please try again later.", proc_pid, proc_user)
        logger.error("Program will exit now.")
        sys.exit(61)
    except Exception as exc:
        logger.error(exc)
        logger.error("Program will exit now.")
        sys.exit(62)


def unlock_inventory(lockpath: str):
    """
    Function responsible for unlocking inventory file, See also lock_inventory
    """

    logger.debug("Started unlock_inventory for lockpath %s.", lockpath)

    try:
        os.remove(lockpath)
        logger.info("Lock %s has been removed.", lockpath)
    except FileNotFoundError:
        logger.error("Requested lock %s was not found. Nothing to do.", lockpath)
        logger.error("Program will exit now.")
        sys.exit(63)
    except Exception as exc:
        logger.error(exc)
        logger.error("Program will exit now.")
        sys.exit(64)


def setup_ansible(setup_hooks, commit, workdir):
    """
    Function responsible for execution of setup_hooks
    It passes the "commit" to the hook if one given, if not the hook should
    checkout the default repo.
    """
    failed = False

    if not commit:
        commit = ""
    for hook in setup_hooks:
        if hook["module"] == "script":
            try:
                hook_env = os.environ.copy()
                hook_env["ANSIBLE_DEPLOY_WORKDIR"] = workdir
                with subprocess.Popen([hook["opts"]["file"], commit],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      env=hook_env) as proc:
                    hook_out = proc.communicate()
                    if proc.returncode != 0:
                        failed = True
            except Exception as e:
                logger.error("Failed executing %s: %s", hook["opts"]["file"], e)
                sys.exit(41)
            else:
                if hook_out != ("", ""):
                    logger.info("setup_hook(%s),\nstdout:\n%s\nstdrr:\n%s", hook["name"],
                                hook_out[0].decode(), hook_out[1].decode())
                    logger.info(hook_out)
                if proc.returncode:
                    logger.error("Setup hook %s failed, cannot continue", hook["name"])
                    sys.exit(40)
                else:
                    logger.info("Setup completed in %s", os.getcwd())

        else:
            logger.error("Not supported")
        if failed:
            sys.exit(69)


def get_playbooks(config: dict, task_name: str):
    """
    Function obtaining play items for specified task.
    :param config:
    :param task_name:
    :return:
    """
    playbooks = []

    for item in config["tasks"]["tasks"]:
        if item["name"] == task_name:
            play_names = item["play_items"]

    for play in play_names:
        for item in config["tasks"]["play_items"]:
            if item["name"] == play:
                playbooks.append(item["file"])

    return playbooks


def run_task(config: dict, options: dict, inventory: str):
    """
    Function implementing actual execution of ansible-playbook
    """
    playbooks = get_playbooks(config, options["task"])
    if len(playbooks) < 1:
        logger.error("No playbooks found for requested task %s. Nothing to do.", options['task'])
        logger.error("Program will exit now.")
        sys.exit(70)
    else:
        for playbook in playbooks:
            command = ["ansible-playbook", "-i", inventory, playbook]
            logger.debug("Running '%s'.", command)
            try:
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as \
                        proc:
                    std_o, std_e = proc.communicate()
                    for line in std_o.split(b"\n\n"):
                        logger.info(line.decode("utf-8"))
                if proc.returncode == 0:
                    logger.info("'%s' ran succesfully", command)
                else:
                    logger.error("'%s' failed due to:", command)
                    for line in std_e.split(b"\n\n"):
                        logger.error(line.decode("utf-8"))
                    logger.error("Program will exit now.")
                    sys.exit(71)
            except Exception as exc:
                logger.error("'%s' failed due to:")
                logger.error(exc)
                logger.error("Program will exit now.")
                sys.exit(72)


def list_tasks(config, options):
    """
    Function listing tasks available to the user limited to given infra/stage/task
    """
    task_list = []
    for item in config["tasks"]["tasks"]:
        task_list.append(item["name"])

    logger.info("  ".join(task_list))


# TODO: At least infra level should be returned from validate options since we do similar check
# (existence) there.
def get_inventory_file(config: dict, options: dict):
    """
    Function returning relativ path to inventory file.
    :param config:
    :param options:
    :return:
    """

    inv_file = None

    for item in config["infra"]:
        if item["name"] == options["infra"]:
            for elem in item["stages"]:
                if elem["name"] == options["stage"]:
                    inv_file = elem["inventory"]

    return inv_file


def load_global_configuration(cfg_path: str):
    """Function responsible for single file loading and validation"""
    if cfg_path:
        pass
    else:
        cfg_path = CONF
    logger.debug("Loading :%s", cfg_path)

    with open(cfg_path, "r", encoding="utf8") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
            logger.debug("Global configuration loaded:")
            logger.debug(str(config))
            return config
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(51)


def main():
    """ansible-deploy endpoint function"""
    global logger, conf

    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.getcwd()
    logger = set_logging(log_dir, LOG_NAME_FRMT, start_ts)
    if len(sys.argv) < 2:
        logger.error("Too few arguments")
        sys.exit(2)

    conf = load_global_configuration(None)

    subcommand = get_sub_command(sys.argv[1])
    options = parse_options(sys.argv[2:])
    required_opts = validate_options(options, subcommand)
    config = load_configuration()
    validate_option_values_against_config(config, options, required_opts)

    if options["dry"]:
        logger.info("Skipping execution because of --dry-run option")
        sys.exit(0)

    if subcommand == "list":
        list_tasks(config, options)
    else:
        lockdir = os.path.join(conf["global_paths"]["work_dir"], "locks")
        inv_file = get_inventory_file(config, options)
        lockpath = os.path.join(lockdir, inv_file.replace("/", "_"))
        if subcommand == "run":
            workdir = create_workdir(start_ts, conf["global_paths"]["work_dir"])
            setup_ansible(config["tasks"]["setup_hooks"], options["commit"], workdir)
            lock_inventory(lockdir, lockpath)
            run_task(config, options, inv_file)
            unlock_inventory(lockpath)
        elif subcommand == "lock":
            lock_inventory(lockdir, lockpath)
        elif subcommand == "unlock":
            unlock_inventory(lockpath)

    sys.exit(0)
