"""Module for validating input data, configuration files and data structures"""

import sys
import os
import re
from ansible_deployer.modules import globalvars


class Validators:
    """Class validating input data, yaml configuration files and their compatibility"""

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def verify_subcommand(command: str, color_flag: bool):
        """Function to check the first arguments for a valid subcommand"""
        if color_flag:
            PRINT_FAIL = PRINT_END = ""
        else:
            PRINT_FAIL = globalvars.PRINT_FAIL
            PRINT_END = globalvars.PRINT_END

        if command not in globalvars.SUBCOMMANDS:
            print(f"{PRINT_FAIL}[CRITICAL]: Unknown subcommand :%s {PRINT_END}", (command),
                  file=sys.stderr)
            sys.exit("55")

    @staticmethod
    def verify_switches(switches: list, color_flag: bool):
        """
        Check if 2nd and following positional arguments are valid
        """
        if color_flag:
            PRINT_FAIL = PRINT_END = ""
        else:
            PRINT_FAIL = globalvars.PRINT_FAIL
            PRINT_END = globalvars.PRINT_END

        if switches[0] != "show" and len(switches[1:]) > 0:
            print(f"{PRINT_FAIL}[CRITICAL]: Too many positional arguments! Only subcommand \"show\""
                  f" can accept following arguments: all, task, infra.{PRINT_END}")
            sys.exit("56")

        for switch in switches[1:]:
            if switch not in ("all", "task", "infra"):
                print(f"{PRINT_FAIL}[CRITICAL]: Invalid argument {switch}! Subcommand \"show\" can"
                      f" accept only following arguments: all, task, infra.{PRINT_END}")
                sys.exit("57")

    def validate_options(self, options: dict):
        """Function checking if the options set are allowed in this subcommand"""
        self.logger.debug("validate_options running for subcommand: %s", options["subcommand"])
        required = []
        notsupported = []

        if options["subcommand"] == "run":
            required = ["task", "infra", "stage"]
            notsupported = ["switches"]
        elif options["subcommand"] == "verify":
            required = ["task", "infra", "stage"]
            notsupported = ["switches", "commit"]
        elif options["subcommand"] in ("lock", "unlock"):
            required = ["infra", "stage"]
            notsupported = ["switches", "task", "commit", "keep_locked", "limit", "raw_output",
                            "self_setup"]
        elif options["subcommand"] == "show":
            notsupported = ["task", "infra", "stage", "commit", "conf_val", "keep_locked", "syslog",
                            "limit", "raw_output", "self_setup"]

        failed = False
        for req in required:
            if not options[req]:
                self.logger.error("Option %s is required for %s", self.expand_option_name(req),
                                  options["subcommand"])
                failed = True

        for notsup in notsupported:
            if options[notsup]:
                self.logger.error("Option %s is not supported by %s",
                                  self.expand_option_name(notsup), options["subcommand"])
                failed = True

        if failed:
            self.logger.critical("Failed to validate options")
            sys.exit(55)

    def validate_option_by_dict_with_name(self, optval: str, conf: dict):
        """
        Validate if given dictionary contains element with name equal to optval
        """
        elem = None
        if optval:
            for elem in conf:
                if elem["name"] == optval:
                    break
            else:
                self.logger.critical("%s not found in configuration file.", optval)
                sys.exit(54)

        return elem

    @staticmethod
    def validate_user_infra_stage():
        """Function checking if user has rights to execute command on selected infrastructure
        Required for: run, lock and unlock operations
        Exit on failure, return inventory on success
        """
        inventory = ""

        return inventory

    @staticmethod
    def validate_user_task():
        """Function checking if user has rights to execute the task
        Rquired for: run"""

        return True

    def validate_checkout(self, options: dict, config: dict):
        """Validate --commit or --self-setup options and return commit/path value"""
        if options["commit"] and options["self_setup"]:
            self.logger.critical("Options --commit and --self-setup are mutually exlcusive!")
            sys.exit(58)
        elif options["self_setup"]:
            commit = self.validate_self_setup(options, config)
        else:
            commit = self.validate_commit(options, config)

        return commit

    def validate_self_setup(self, options: dict, config: dict):
        """Validate if --self-setup is allowed and if requested path exists"""
        if os.path.exists(options["self_setup"]):
            for infra in config["infra"]:
                if infra["name"] == options["infra"]:
                    for stage in infra["stages"]:
                        if stage["name"] == options["stage"]:
                            allow = stage.get("allow_user_checkout", None)
                            if not allow:
                                self.logger.critical("Self setup is not allowed for infra %s!",
                                                     infra["name"])
                                sys.exit(59)
                            else:
                                ret = options["self_setup"]
        else:
            self.logger.critical("Provided --self-setup path %s does not exist!",
                                 options["self_setup"])
            sys.exit(59)

        return ret

    def validate_commit(self, options: dict, config: dict):
        """Function to validate commit value against config and assign final value"""
        if not options["commit"]:
            commit_id = None
            self.logger.debug("Using default commit.")
        else:
            for item in config["tasks"]["tasks"]:
                if item["name"] == options["task"]:
                    for elem in item["allowed_for"]:
                        available_commits = elem.get("commit", [])
                        for commit in available_commits:
                            if re.fullmatch(commit, options["commit"]):
                                commit_id = commit
                                self.logger.debug("Using commit: %s .", commit_id)
                                break
                        else:
                            continue
                        break
                    else:
                        self.logger.error("Requested commit %s is not valid for task %s.",
                                     options["commit"], options["task"])
                        self.logger.error("Program will exit now.")
                        sys.exit(56)

        return commit_id

    def validate_option_values_against_config(self, config: dict, options: dict):
        """
        Function responsible for checking if option values match configuration
        """
        selected_items = {}
        for option in options.keys():
            if options[option]:
                if option == "infra":
                    selected_items["infra"] = self.validate_option_by_dict_with_name(
                                              options["infra"], config["infra"])
                elif option == "task":
                    selected_items["task"] = self.validate_option_by_dict_with_name(options["task"],
                                             config["tasks"]["tasks"])
                elif option == "stage":
                    for item in config["infra"]:
                        if item["name"] == options["infra"]:
                            index = config["infra"].index(item)
                    selected_items["stage"] = self.validate_option_by_dict_with_name(
                                              options["stage"], config["infra"][index]["stages"])
                elif option == "limit":
                    for item in config["tasks"]["tasks"]:
                        if item["name"] == options["task"]:
                            allow_limit = item.get("allow_limit", False)
                            if allow_limit:
                                selected_items["limit"] = options["limit"]
                                break
                    else:
                        self.logger.critical("Limit %s is not available for task %s.",
                                             options["limit"], options["task"])
                        sys.exit(54)

        selected_items["commit"] = self.validate_checkout(options, config)
        self.logger.debug("Completed validate_option_values_with_config")

                #TODO: validate if user is allowed to use --commit
                #TODO: validate if user is allowed to execute the task on infra/stag pair
                #(validate_user_infra_stage(), validate_usr_task())

        return selected_items

    def verify_task_permissions(self, selected_items: dict, user_groups: list, config: dict):
        """
        Function verifies if the running user is allowed to run the task
        """
        s_task = selected_items["task"]
        s_infra = selected_items["infra"]
        o_stage = selected_items["stage"]
        self.logger.debug("Running verify_task_permissions for s_task:\n%s,\ns_infra:\n%s,\n"
                          "o_stage:\n%s\n and user groups:\n%s", s_task, s_infra, o_stage,
                          user_groups)

        for item in s_task["allowed_for"]:
            acl_group = item["acl_group"]
            self.logger.debug("\tChecking permission group: %s, for user_groups: %s", acl_group,
                              user_groups)
            self.logger.debug("\tPermission group %s content: %s", acl_group,
                              str(config["acl"][acl_group]))
            if any(group in user_groups for group in config["acl"][acl_group]["groups"]):
                for infra in config["acl"][acl_group]["infra"]:
                    self.logger.debug("\t\tChecking infra: %s for infra: %s", infra,
                                 selected_items["infra"]["name"])
                    if infra["name"] == selected_items["infra"]["name"]:
                        for stage in infra["stages"]:
                            self.logger.debug("\t\t\tChecking stage: %s for stage: %s", stage,
                                              o_stage["name"])
                            if stage == o_stage["name"]:
                                self.logger.debug("Task allowed, based on %s", acl_group)
                                return True
        self.logger.debug("Task forbidden")
        return False

    @staticmethod
    def expand_option_name(option: str):
        """Expand name of option variable name to option argument name"""
        if option in ["conf_val", "infra", "raw_output"]:
            option = globalvars.OPTION_EXPANSION[option]

        formatted_option = "--" + option.replace("_", "-")
        return formatted_option
