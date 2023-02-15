"""Module for running system processes"""

import os
import sys
import subprocess
from ansible_deployer.modules.outputs.formatting import Formatters

class Runners:
    """Class handling ansible hooks and ansible plays execution"""

    def __init__(self, logger, lock_obj, workdir, start_ts_raw, setup_hooks):
        self.logger = logger
        self.lock_obj = lock_obj
        self.workdir = workdir
        self.start_ts_raw = start_ts_raw
        self.setup_hooks = setup_hooks
        self.sequence_id = os.path.basename(self.workdir)

    @staticmethod
    def reassign_commit_and_workdir(commit: str, workdir: str):
        """Change workdir if commit is a path (option --self-setup enabled in main)"""
        if not commit:
            commit = ""
        elif os.path.exists(os.path.abspath(commit)):
            workdir = commit
            commit = ""

        return workdir, commit

    def setup_ansible(self, commit: str, conf_dir: str):
        """
        Function responsible for execution of setup_hooks
        It passes the "commit" to the hook if one given, if not the hook should
        checkout the default repo.
        """
        failed = False
        workdir, commit = Runners.reassign_commit_and_workdir(commit, self.workdir)

        for hook in self.setup_hooks:
            if hook["module"] == "script":
                try:
                    with subprocess.Popen([os.path.join(conf_dir, hook["opts"]["file"]), commit],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE, cwd=workdir) as proc:
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

    def run_playitem(self, config: dict, options: dict, inventory: str, lockpath: str, db_writer):
        """
        Function implementing actual execution of runner [ansible-playbook or py.test]
        """
        playitems = self.get_playitems(config, options)
        host_list = []
        returned = []
        if not playitems:
            self.logger.critical("No playitems found for requested task %s. Nothing to do.",
                                 options['task'])
            self.lock_obj.unlock_inventory(lockpath)
            sequence_records = db_writer.start_sequence_dict([""], self.setup_hooks, options,
                                                             self.start_ts_raw, self.sequence_id)
            db_writer.finalize_db_write(sequence_records, False)
            sys.exit(70)
        else:
            for playitem in playitems:
                command, command_env = self.construct_command(playitem, inventory, config, options)
                self.logger.debug("Running '%s'.", command)
                try:
                    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          env=command_env) as proc:

                        for msg in proc.stdout:
                            dec_msg = msg.split(b"\n")[0].decode("utf-8")
                            returned.append(dec_msg)
                            if options["raw_output"]:
                                print(dec_msg)

                        proc.communicate()
                        format_obj = Formatters(self.logger)
                        parsed_std = format_obj.format_ansible_output(returned)
                        play_host_list = db_writer.write_records(db_writer.parse_yaml_output(
                            parsed_std["complete"], self.sequence_id))
                        for host in play_host_list:
                            host_list.append(host)
                        sequence_records = db_writer.start_sequence_dict(host_list,
                                                                         self.setup_hooks, options,
                                                                         self.start_ts_raw,
                                                                         self.sequence_id)

                        if proc.returncode == 0:
                            format_obj.positive_ansible_output(parsed_std["warning"],
                                                               parsed_std["output"], command)
                        else:
                            format_obj.negative_ansible_output(parsed_std["warning"],
                                                               parsed_std["error"], command)
                            self.lock_obj.unlock_inventory(lockpath)
                            db_writer.finalize_db_write(sequence_records, False)
                            self.logger.critical("Program will exit now.")
                            sys.exit(71)
                except Exception as exc:
                    self.logger.critical("\"%s\" failed due to:")
                    self.logger.critical(exc)
                    sequence_records = db_writer.start_sequence_dict(host_list, self.setup_hooks,
                                                                     options, self.start_ts_raw,
                                                                     self.sequence_id)
                    db_writer.finalize_db_write(sequence_records, True)
                    sys.exit(72)
            return sequence_records

    @staticmethod
    def get_tags_for_task(config: dict, options: dict):
        """Function to get task's tags"""
        tags = []
        for task in config["tasks"]["tasks"]:
            if task["name"] == options["task"]:
                tags = task.get("tags", [])

        if options["dry_mode"]:
            tags.append("ansible_deployer_dry_mode")

        return tags

    @staticmethod
    def construct_command(playitem: str, inventory: str, config: dict, options: dict):
        """Create final ansible command from available variables"""
        tags = Runners.get_tags_for_task(config, options)

        if "runner" in playitem and playitem["runner"] == "py.test":
            command = ["py.test", "--ansible-inventory", inventory]
            if options["limit"]:
                command.append(f"--hosts='ansible://{options['limit']}'")
            else:
                command.append("--hosts=ansible://all")
            command.append("--junit-xml=junit_"+options['task']+'.xml')
            command.append("./"+playitem["file"])
            command_env = os.environ
        else:
            command = ["ansible-playbook", "-v", "-i", inventory, playitem["file"]]
            if options["limit"]:
                command.append("-l")
                command.append(options["limit"])
            if tags:
                command.append("-t")
                command.append(",".join(tags))
            if options["check_mode"]:
                command.append("-C")
            command_env=dict(os.environ, ANSIBLE_STDOUT_CALLBACK="yaml", ANSIBLE_NOCOWS="1",
                             ANSIBLE_LOAD_CALLBACK_PLUGINS="1")

        return command, command_env
