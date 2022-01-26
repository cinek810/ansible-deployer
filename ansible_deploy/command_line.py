"""Main module for ansible-deploy"""

import sys

def get_sub_command():
    """Function to check the first arguments (argv[1..]) looking for a subcommand"""

def parse_options():
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""

def validate_options(options, subcommand):
    """Function checking if the options set are allowed in this subcommand"""
    if subcommand == "run":
        if "task" not in options:
            return False
    return True

def load_configuration():
    """Function responsible for reading configuration files and running a schema validator against
    it"""

def validate_user_infra_stage():
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations"""

def validate_user_task():
    """Function checking if user has rights to execute the task
    Rquired for: run"""

def main():
    """ansible-deploy endpoint function"""
    sys.exit(0)
