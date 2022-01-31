"""Main module for ansible-deploy"""

import sys
import os
import argparse
import logging
import datetime
#TODO: Add an option to explicitly enable syslog logging
#from logging import handlers as log_han

import yaml
from cerberus import Validator


LOGNAME = "ansible-deploy_execution_{}.log"
SEQUENCE_PREFIX = "SEQ"
WORKDIR = "/tmp"
CONF_DIR = "/etc/ansible-deploy/"


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
    console_handler.setLevel(logging.INFO)
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

    arguments = parser.parse_args(argv)

    options = {}
    options["infra"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]

    return options

def create_workdir(timestamp: str, base_dir: str):
    """Function to create working directory on filesystem"""
    short_ts = timestamp.split("_")[0]
    date_dir = os.path.join(base_dir, short_ts)

    #
    #TODO: Add locking of the directory

    if short_ts not in os.listdir(base_dir):
        seq_path = os.path.join(date_dir, f"{SEQUENCE_PREFIX}0000")
    else:
        sequence_list = os.listdir(date_dir)
        sequence_list.sort()
        new_sequence = int(sequence_list[-1].split(SEQUENCE_PREFIX)[1]) + 1
        seq_path = os.path.join(date_dir, f"{SEQUENCE_PREFIX}{new_sequence:04d}")

    os.makedirs(seq_path)
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

def load_configuration_file(config_file):
    """Function responsible for single file loading and validation"""
    #TODO: Add verification of owner/group/persmissions
    logger.debug("Loading :%s", config_file)

    with open(CONF_DIR+config_file, "r", encoding="utf8") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(51)

    with open(CONF_DIR+"schema/"+config_file, "r", encoding="utf8") as schema_stream:
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

    infra = load_configuration_file("infra.yaml")

    config = {}
    config["infra"] = infra["infrastructures"]
    return config

def validate_option_by_dict_with_name(option, conf_dict):
    if option:
        for elem in conf_dict:
            if elem["name"] == option:
                break
        else:
            logger.error("%s not found in configuration file.", option)
            sys.exit(54)

def validate_option_values_with_config(config, options):
    """
    Function responsible for checking if option values match configuration
    """
    validate_option_by_dict_with_name(options["infra"], config["infra"])
    validate_option_by_dict_with_name(options["task"], config["tasks"]["tasks"])

def validate_user_infra_stage():
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations"""

def validate_user_task():
    """Function checking if user has rights to execute the task
    Rquired for: run"""

def main():
    """ansible-deploy endpoint function"""

    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    global logger
    log_dir = os.getcwd()
    logger = set_logging(log_dir, LOGNAME, start_ts)
    if len(sys.argv) < 2:
        logger.error("To fee arguments")
        sys.exit(2)

    subcommand = get_sub_command(sys.argv[1])
    options = parse_options(sys.argv[2:])
    validate_options(options, subcommand)
    config = load_configuration()
    validate_option_values_with_config(config, options)

    #create_workdir(start_ts, WORKDIR)
    sys.exit(0)
