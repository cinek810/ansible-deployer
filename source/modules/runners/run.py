"""Module for running system processes"""

import os
import sys
import subprocess
from ansible_deployer.modules.outputs.formatting import Formatters

class Runners:
    """Class handling ansible hooks and ansible plays execution"""

    def __init__(self, logger, lock_obj):
        self.logger = logger
        self.lock_obj = lock_obj

    @staticmethod
    def reassign_commit_and_workdir(commit: str, workdir: str):
        """Change workdir if commit is a path (option --self-setup enabled in main)"""
        if not commit:
            commit = ""
        elif os.sep in commit:
            workdir = commit
            commit = ""

        return workdir, commit

    def setup_ansible(self, setup_hooks: list, commit: str, workdir: str):
        """
        Function responsible for execution of setup_hooks
        It passes the "commit" to the hook if one given, if not the hook should
        checkout the default repo.
        """
        failed = False
        workdir, commit = Runners.reassign_commit_and_workdir(commit, workdir)

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
                        std_out, std_err = proc.communicate()
                        if proc.returncode != 0:
                            failed = True
                except Exception as e:
                    self.logger.critical("Failed executing %s: %s", hook["opts"]["file"], e)
                    sys.exit(41)
                else:
                    if std_out:
                        self.logger.info("Setup hook %s stdout:", hook["name"])
                        for line in std_out.split(b"\n"):
                            if line:
                                self.logger.info(line.decode("utf-8"))
                    if std_err:
                        self.logger.error("Setup hook %s stderr:", hook["name"])
                        for line in std_err.split(b"\n"):
                            if line:
                                self.logger.error(line.decode("utf-8"))
                    if proc.returncode:
                        self.logger.critical("Setup hook %s failed, cannot continue", hook["name"])
                        sys.exit(40)
                    else:
                        self.logger.info("Setup completed in %s", workdir)

            else:
                self.logger.error("Not supported")
            if failed:
                self.logger.critical("Program will exit now.")
                sys.exit(69)

    def get_playitems(self, config: dict, options: dict):
        """
        Function obtaining play items for specified task.
        :param config:
        :param task_name:
        :return:
        """
        playitems = []

        for item in config["tasks"]["tasks"]:
            if item["name"] == options["task"]:
                if options["subcommand"] == "run":
                    play_names = item["play_items"]
                elif options["subcommand"] == "verify":
                    play_names = item["verify_items"]
                else:
                    self.logger.critical("Should have never happen. Uncleaned lock left")
                    sys.exit(130)

        for play in play_names:
            for item in config["tasks"]["play_items"]:
                if item["name"] == play:
                    skip = item.get("skip", [])
                    if skip:
                        for elem in item["skip"]:
                            if elem["infra"] == options["infra"] and \
                                elem["stage"] == options["stage"]:
                                self.logger.info("Skipping playitem %s on %s and %s stage.", play,
                                            options["infra"], options["stage"])
                                break
                        else:
                            playitems.append(item)
                    else:
                        playitems.append(item)

        # TODO add check if everything was skipped
        return playitems

    def run_playitem(self, config: dict, options: dict, inventory: str, lockpath: str):
        """
        Function implementing actual execution of runner [ansible-playbook or py.test]
        """
        playitems = self.get_playitems(config, options)
        if not playitems:
            self.logger.critical("No playitems found for requested task %s. Nothing to do.",
                                 options['task'])
            self.lock_obj.unlock_inventory(lockpath)
            sys.exit(70)
        else:
            for playitem in playitems:
                command = self.construct_command(playitem, inventory, config, options)
                self.logger.debug("Running '%s'.", command)
                try:
                    with subprocess.Popen(command, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE) as proc:
                        returned = proc.communicate()
                        format_obj = Formatters(self.logger)
                        if options["raw_output"]:
                            if proc.returncode != 0:
                                if options["debug"]:
                                    format_obj.debug_std_out(returned[0])
                                self.logger.error("'%s' failed due to:", command)
                                format_obj.format_std_err(returned[1])
                                self.lock_obj.unlock_inventory(lockpath)
                                self.logger.critical("Program will exit now.")
                                sys.exit(71)
                            else:
                                if options["debug"]:
                                    format_obj.debug_std_err(returned[1])
                                format_obj.format_std_out(returned[0])
                                self.logger.info("'%s' ran succesfully", command)
                        else:
                            output, warning, error = Formatters.format_ansible_output(returned)
                            if options["debug"]:
                                format_obj.debug_std_out(returned[0])
                                format_obj.format_std_err(returned[1])
                            if proc.returncode == 0:
                                format_obj.positive_ansible_output(warning, output, command)
                            else:
                                format_obj.negative_ansible_output(warning, error, command)
                                self.lock_obj.unlock_inventory(lockpath)
                                self.logger.critical("Program will exit now.")
                                sys.exit(71)
                except Exception as exc:
                    self.logger.critical("\"%s\" failed due to:")
                    self.logger.critical(exc)
                    sys.exit(72)

    @staticmethod
    def get_tags_for_task(config: dict, options: dict):
        """Function to get task's tags"""
        tags = []
        for task in config["tasks"]["tasks"]:
            if task["name"] == options["task"]:
                tags = task.get("tags", [])

        return tags

    @staticmethod
    def construct_command(playitem: str, inventory: str, config: dict, options: dict):
        """Create final ansible command from available variables"""
        tags = Runners.get_tags_for_task(config, options)

        if "runner" in playitem and playitem["runner"] == "py.test":
            command = ["py.test", "--ansible-inventory", inventory]
            if options["limit"]:
                command.append("--hosts='ansible://")
                command.append(options["limit"]+"'")
            else:
                command.append("--hosts=ansible://all")
            command.append("--junit-xml=junit_"+options['task']+'.xml')
            command.append("./"+playitem["file"])
        else:
            command = ["ansible-playbook", "-i", inventory, playitem["file"]]
            if options["limit"]:
                command.append("-l")
                command.append(options["limit"])
            if tags:
                command.append("-t")
                command.append(",".join(tags))

        return command
