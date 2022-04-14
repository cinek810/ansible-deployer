"""Module for validating input data, configuration files and data structures"""

import sys
import re
from ansible_deployer.modules.globalvars import SUBCOMMANDS


class Validators:
    """Class validating input data, yaml configuration files and their compatibility"""

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def verify_subcommand(command: str):
        """Function to check the first arguments for a valid subcommand"""
        if command not in SUBCOMMANDS:
            print("[CRITICAL]: Unknown subcommand :%s", (command), file=sys.stderr)
            sys.exit("55")

    @staticmethod
    def verify_switches(switches: list):
        """
        Check if 2nd and following positional arguments are valid
        """
        if switches[0] != "show" and len(switches[1:]) > 0:
            print("[CRITICAL]: Too many positional arguments! Only subcommand \"show\" can accept"
                  " following arguments: task, infra.")
            sys.exit("56")

        for switch in switches[1:]:
            if switch not in ("task", "infra"):
                print(f"[CRITICAL]: Invalid argument {switch}! Subcommand \"show\" can accept only"
                      " following arguments: task, infra.")
                sys.exit("57")

    def validate_options(self, options: dict):
        """Function checking if the options set are allowed in this subcommand"""
        self.logger.debug("validate_options running for subcommand: %s", options["subcommand"])
        required = []
        notsupported = []

        if options["subcommand"] == "run":
            required = ["task", "infra", "stage"]
        elif options["subcommand"] == "verify":
            required = ["task", "infra", "stage"]
            notsupported = ["commit"]
        elif options["subcommand"] in ("lock", "unlock"):
            required = ["infra", "stage"]
            notsupported = ["task", "commit", "limit"]
        elif options["subcommand"] == "list":
            notsupported = ["commit", "limit"]
        elif options["subcommand"] == "show":
            notsupported = ["commit", "limit"]

        failed = False
        for req in required:
            if options[req] is None:
                self.logger.error("%s is required for %s", req, options["subcommand"])
                failed = True

        for notsup in notsupported:
            if options[notsup] is not None:
                self.logger.error("%s is not supported by %s", notsup, options["subcommand"])
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

        selected_items["commit"] = self.validate_commit(options, config)
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
            if config["acl"][acl_group]["group"] in user_groups:
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
