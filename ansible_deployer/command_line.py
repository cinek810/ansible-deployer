"""Main module for ansible-deploy"""

import sys
import os
import stat
import re
import argparse
import logging
import datetime
import subprocess
import pwd
import grp
import errno
from logging import handlers as log_han
import yaml
from cerberus import Validator


APP_CONF = "/etc/ansible-deploy"
CFG_PERMISSIONS = "0o644"
SUBCOMMANDS = ("run", "list", "lock", "unlock", "verify")

def verify_subcommand(command: str):
    """Function to check the first arguments for a valid subcommand"""
    if command not in SUBCOMMANDS:
        print("[CRITICAL]: Unknown subcommand :%s", (command), file=sys.stderr)
        sys.exit("55")

def set_logging(options: dict):
    """Function to create logging objects"""
    logger = logging.getLogger("ansible-deployer_log")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    console_formatter = logging.Formatter("\n%(asctime)s [%(levelname)s]: %(message)s\n")

    if options["syslog"]:
        rsys_handler = log_han.SysLogHandler(address="/dev/log")
        rsys_handler.setFormatter(formatter)
        rsys_handler.setLevel(logging.WARNING)
        logger.addHandler(rsys_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG if options["debug"] else logging.INFO)
    logger.addHandler(console_handler)

    return logger

def set_logging_to_file(log_dir: str, timestamp: str):
    """Function adding file handler to existing logger"""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir,
                            conf["file_naming"]["log_file_name_frmt"].format(timestamp))
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

def parse_options(argv):
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument("subcommand", nargs='?', default=None, metavar="SUBCOMMAND",
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
        print("[CRITICAL]: First positional argument (subcommand) is required! Available commands "
              "are: run, list, lock, unlock.")
        sys.exit(57)

    options = {}
    options["subcommand"] = arguments.subcommand.lower()
    verify_subcommand(options["subcommand"])
    options["infra"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]
    options["dry"] = arguments.dry
    options["debug"] = arguments.debug
    options["syslog"] = arguments.syslog
    options["limit"] = arguments.limit[0]
    options["conf_dir"] = arguments.conf_dir[0]


    arguments = parser.parse_args(argv)

    if not arguments.subcommand:
        print("[CRITICAL]: First positional argument (subcommand) is required! Available commands "
              "are: run, list, lock, unlock.")
        sys.exit(57)

    options["subcommand"] = arguments.subcommand.lower()
    verify_subcommand(options["subcommand"])

    return options

def create_workdir(timestamp: str):
    """
    Function to create working directory on file system, we expect it to change
    the cwd to newly created workdir at the end.
    """
    short_ts = timestamp.split("_")[0]
    date_dir = os.path.join(conf["global_paths"]["work_dir"], short_ts)

    #
    #TODO: Add locking of the directory

    if short_ts not in os.listdir(conf["global_paths"]["work_dir"]):
        seq_path = os.path.join(date_dir, f"{conf['file_naming']['sequence_prefix']}0000")
        try:
            os.mkdir(date_dir)
            os.chmod(date_dir, int(conf["permissions"]["parent_workdir"].split("o")[1], 8))
            logger.debug("Successfully created parent work dir: %s", seq_path)
        except Exception as e:
            logger.critical("Failed to create parent work dir: %s error was: %s", seq_path, e,
                            file=sys.stderr)
            sys.exit(90)
    else:
        sequence_list = os.listdir(date_dir)
        sequence_list.sort()
        new_sequence = int(sequence_list[-1].split(conf['file_naming']['sequence_prefix'])[1]) + 1
        seq_path = os.path.join(date_dir, f"{conf['file_naming']['sequence_prefix']}"
                                          f"{new_sequence:04d}")

    try:
        os.mkdir(seq_path)
        os.chdir(seq_path)
    except Exception as e:
        logger.critical("Failed to create work dir: %s error was: %s", seq_path, e, file=sys.stderr)
        sys.exit(91)
    logger.debug("Successfully created workdir: %s", seq_path)
    return seq_path

def validate_options(options: dict):
    """Function checking if the options set are allowed in this subcommand"""
    logger.debug("validate_options running for subcommand: %s", options["subcommand"])
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

    failed = False
    for req in required:
        if options[req] is None:
            logger.error("%s is required for %s", req, options["subcommand"])
            failed = True

    for notsup in notsupported:
        if options[notsup] is not None:
            logger.error("%s is not supported by %s", notsup, options["subcommand"])
            failed = True

    if failed:
        logger.critical("Failed to validate options")
        sys.exit(55)

def load_configuration_file(config_path: str):
    """Function responsible for single file loading and validation"""
    #TODO: Add verification of owner/group/persmissions
    check_cfg_permissions_and_owner(config_path)
    config_file = os.path.basename(config_path)
    logger.debug("Loading :%s", config_file)

    with open(config_path, "r", encoding="utf8") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as e:
            logger.critical("Yaml loading failed for %s due to %s.", config_path, e)
            sys.exit(51)

    schema_path = os.path.join(APP_CONF, "schema", config_file)
    with open(schema_path, "r", encoding="utf8") as schema_stream:
        try:
            schema = yaml.safe_load(schema_stream)
        except yaml.YAMLError as e:
            logger.critical("Yaml loading failed for %s due to %s.", config_path, e)
            sys.exit(52)

    validator = Validator(schema)
    if not validator.validate(config, schema):
        logger.critical("Yaml validation failed for %s due to %s.", config_path, validator.errors)
        sys.exit(53)

    logger.debug("Loaded:\n%s", str(config))
    return config

def check_cfg_permissions_and_owner(cfg_path: str):
    """Function to verify permissions and owner for config files"""
    stat_info = os.stat(cfg_path)

    if stat_info.st_uid == 0:
        if oct(stat.S_IMODE(stat_info.st_mode)) == CFG_PERMISSIONS:
            logger.debug("Correct permissions and owner for config file %s.", cfg_path)
        else:
            logger.error("File %s permissions are incorrect! Contact your sys admin.", cfg_path)
            logger.error("Program will exit now.")
            sys.exit(40)
    else:
        logger.error("File %s owner is not root! Contact your sys admin.", cfg_path)
        logger.error("Program will exit now.")
        sys.exit(41)

def get_config_paths(config_dir):
    """Function to create absolute config paths and check their extension compatibility"""
    ymls = []
    yamls = []
    infra_cfg = None
    tasks_cfg = None
    acl_cfg = None

    for config in os.listdir(config_dir):
        if config != "ansible-deploy.yaml":
            if config.endswith(".yml"):
                ymls.append(config)
            elif config.endswith(".yaml"):
                yamls.append(config)

            if config.startswith("infra"):
                infra_cfg = os.path.join(config_dir, config)
            elif config.startswith("tasks"):
                tasks_cfg = os.path.join(config_dir, config)
            elif config.startswith("acl"):
                acl_cfg = os.path.join(config_dir, config)
                tasks_cfg = os.path.join(config_dir, config)

    if len(ymls) > 0 and len(yamls) > 0:
        logger.debug("Config files with yml extensions: %s", " ".join(ymls))
        logger.debug("Config files with yaml extensions: %s", " ".join(yamls))
        logger.critical("Config files with different extensions (.yml and .yaml) are not allowed "
                        "in conf dir %s !", config_dir)
        sys.exit(42)

    if not infra_cfg:
        logger.critical("Infrastructure configuration file does not exist in %s!",
                        config_dir)
        sys.exit(43)

    if not tasks_cfg:
        logger.critical("Tasks configuration file does not exist in %s!",
                        config_dir)
        sys.exit(44)

    if not acl_cfg:
        logger.critical("Permission configuration file does not exist in %s!",
                        conf["global_paths"]["config_dir"])
        sys.exit(45)

    return infra_cfg, tasks_cfg, acl_cfg

def load_configuration(conf_dir):
    """Function responsible for reading configuration files and running a schema validator against
    it
    """
    logger.debug("load_configuration called")
    #TODO: validate files/directories permissions - should be own end editable only by special user
    infra_cfg, tasks_cfg, acl_cfg = get_config_paths(conf_dir)

    infra = load_configuration_file(infra_cfg)
    tasks = load_configuration_file(tasks_cfg)
    acl = load_configuration_file(acl_cfg)

    config = {}
    config["infra"] = infra["infrastructures"]
    config["tasks"] = tasks

    config["acl"] = {}
    for group in acl["acl_lists"]:
        key = group["name"]
        group.pop("name")
        config["acl"][key] = group

    return config

def validate_option_by_dict_with_name(optval: str, conf: dict):
    """
    Validate if given dictionary contains element with name equal to optval
    """
    elem = None
    if optval:
        for elem in conf:
            if elem["name"] == optval:
                break
        else:
            logger.critical("%s not found in configuration file.", optval)
            sys.exit(54)

    return elem

def validate_user_infra_stage():
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations
    Exit on failure, return inventory on success
    """
    inventory = ""

    return inventory

def validate_user_task():
    """Function checking if user has rights to execute the task
    Rquired for: run"""

def validate_commit(options: dict, config: dict):
    """Function to validate commit value against config and assign final value"""
    if not options["commit"]:
        commit_id = None
        logger.debug("Using default commit.")
    else:
        for item in config["tasks"]["tasks"]:
            if item["name"] == options["task"]:
                for elem in item["allowed_for"]:
                    available_commits = elem.get("commit", [])
                    for commit in available_commits:
                        if re.fullmatch(commit, options["commit"]):
                            commit_id = commit
                            logger.debug("Using commit: %s .", commit_id)
                            break
                    else:
                        continue
                    break
                else:
                    logger.error("Requested commit %s is not valid for task %s.",
                                 options["commit"], options["task"])
                    logger.error("Program will exit now.")
                    sys.exit(56)

    return commit_id

def validate_option_values_against_config(config: dict, options: dict):
    """
    Function responsible for checking if option values match configuration
    """
    selected_items = {}
    for option in options.keys():
        if options[option]:
            if option == "infra":
                selected_items["infra"] = validate_option_by_dict_with_name(options["infra"],
                                                                            config["infra"])
            elif option == "task":
                selected_items["task"] = validate_option_by_dict_with_name(options["task"],
                                                                           config["tasks"]["tasks"])
            elif option == "stage":
                for item in config["infra"]:
                    if item["name"] == options["infra"]:
                        index = config["infra"].index(item)
                selected_items["stage"] = validate_option_by_dict_with_name(options["stage"],\
                                                                config["infra"][index]["stages"])
            elif option == "limit":
                for item in config["tasks"]["tasks"]:
                    if item["name"] == options["task"]:
                        allow_limit = item.get("allow_limit", False)
                        if allow_limit:
                            selected_items["limit"] = options["limit"]
                            break
                else:
                    logger.critical("Limit %s is not available for task %s.", options["limit"],
                                    options["task"])
                    sys.exit(54)

    selected_items["commit"] = validate_commit(options, config)
    logger.debug("Completed validate_option_values_with_config")

            #TODO: validate if user is allowed to use --commit
            #TODO: validate if user is allowed to execute the task on infra/stag pair
            #(validate_user_infra_stage(), validate_usr_task())

    return selected_items

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
        logger.critical("Another process (PID: %s) started by user %s is using this infrastructure"
                        ", please try again later.", proc_pid.strip(), proc_user.strip())
        sys.exit(61)
    except Exception as exc:
        logger.critical(exc)
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
        logger.critical("Requested lock %s was not found. Nothing to do.", lockpath)
        sys.exit(63)
    except Exception as exc:
        logger.critical(exc)
        sys.exit(64)

def setup_ansible(setup_hooks: list, commit: str, workdir: str):
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
                    std_out, std_err = proc.communicate()
                    if proc.returncode != 0:
                        failed = True
            except Exception as e:
                logger.critical("Failed executing %s: %s", hook["opts"]["file"], e)
                sys.exit(41)
            else:
                if std_out:
                    logger.info("Setup hook %s stdout:", hook["name"])
                    for line in std_out.split(b"\n"):
                        if line:
                            logger.info(line.decode("utf-8"))
                if std_err:
                    logger.error("Setup hook %s stderr:", hook["name"])
                    for line in std_err.split(b"\n"):
                        if line:
                            logger.error(line.decode("utf-8"))
                if proc.returncode:
                    logger.critical("Setup hook %s failed, cannot continue", hook["name"])
                    sys.exit(40)
                else:
                    logger.info("Setup completed in %s", os.getcwd())

        else:
            logger.error("Not supported")
        if failed:
            logger.critical("Program will exit now.")
            sys.exit(69)

def get_playitems(config: dict, options: dict):
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
                logger.critical("Should have never happen. Uncleaned lock left")
                sys.exit(130)

    for play in play_names:
        for item in config["tasks"]["play_items"]:
            if item["name"] == play:
                skip = item.get("skip", [])
                if skip:
                    for elem in item["skip"]:
                        if elem["infra"] == options["infra"] and elem["stage"] == options["stage"]:
                            logger.info("Skipping playitem %s on %s and %s stage.", play,
                                        options["infra"], options["stage"])
                            break
                    else:
                        playitems.append(item)
                else:
                    playitems.append(item)

    # TODO add check if everything was skipped
    return playitems

def run_playitem(config: dict, options: dict, inventory: str, lockpath: str):
    """
    Function implementing actual execution of runner [ansible-playbook or py.test]
    """
    playitems = get_playitems(config, options)
    tags = get_tags_for_task(config, options)
    if len(playitems) < 1:
        logger.critical("No playitems found for requested task %s. Nothing to do.", options['task'])
        unlock_inventory(lockpath)
        sys.exit(70)
    elif playitems is not None:
        for playitem in playitems:
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
                    tag_string = ",".join(tags)
                    command.append("-t")
                    command.append(tag_string)
            logger.debug("Running '%s'.", command)
            try:
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as \
                        proc:
                    output, warning, error = format_ansible_output(proc.communicate())
                if proc.returncode == 0:
                    positive_ansible_output(warning, output, command)
                else:
                    negative_ansible_output(warning, error, command)
                    unlock_inventory(lockpath)
                    logger.critical("Program will exit now.")
                    sys.exit(71)
            except Exception as exc:
                logger.critical("\"%s\" failed due to:")
                logger.critical(exc)
                sys.exit(72)
    else:
        logger.error("No playitems defined for action")
        unlock_inventory(lockpath)
        sys.exit(errno.ENOENT)

def positive_ansible_output(warning: list, output: list, command: str):
    """Log output for a positive case in ansible execution"""
    if warning:
        for line in warning:
            logger.warning(line)
    if output:
        for line in output:
            logger.info(line)
    logger.info("\"%s\" ran succesfully", " ".join(command))

def negative_ansible_output(warning: list, error: list, command: str):
    """Log output for a negative case in ansible execution"""
    if warning:
        for line in warning:
            logger.warning(line)
    logger.error("\"%s\" failed due to:", " ".join(command))
    if error:
        for line in error:
            logger.error(line)

def format_ansible_output(proces_output):
    """Group and format output from ansible execution"""
    std_out, std_err = proces_output
    std_output = []
    std_warning = []
    std_error = []
    for line in std_out.split(b"\n\n"):
        dec_line = line.decode("utf-8")
        if "fatal" in dec_line.lower() or "err" in dec_line.lower():
            std_error.append(dec_line)
        elif "warn" in dec_line.lower():
            std_warning.append(dec_line)
        else:
            std_output.append(dec_line)

    for line in std_err.split(b"\n\n"):
        dec_line = line.decode("utf-8")
        if "fatal" in dec_line.lower() or "err" in dec_line.lower():
            std_error.append(dec_line)
        elif "warn" in dec_line.lower():
            std_warning.append(dec_line)
        else:
            std_output.append(dec_line)

    return std_output, std_warning, std_error

def verify_task_permissions(selected_items: dict, user_groups: list, config: dict):
    """
    Function verifies if the running user is allowed to run the task
    """
    s_task = selected_items["task"]
    s_infra = selected_items["infra"]
    o_stage = selected_items["stage"]
    logger.debug("Running verify_task_permissions for s_task:\n%s,\ns_infra:\n%s,\no_stage:\n%s\n"
                "and user groups:\n%s", s_task, s_infra, o_stage, user_groups)

    for item in s_task["allowed_for"]:
        acl_group = item["acl_group"]
        logger.debug("\tChecking permission group: %s, for user_groups: %s", acl_group, user_groups)
        logger.debug("\tPermission group %s content: %s", acl_group, str(config["acl"][acl_group]))
        if config["acl"][acl_group]["group"] in user_groups:
            for infra in config["acl"][acl_group]["infra"]:
                logger.debug("\t\tChecking infra: %s for infra: %s", infra,
                             selected_items["infra"]["name"])
                if infra["name"] == selected_items["infra"]["name"]:
                    for stage in infra["stages"]:
                        logger.debug("\t\t\tChecking stage: %s for stage: %s", stage,
                                    o_stage["name"])
                        if stage == o_stage["name"]:
                            logger.debug("Task allowed, based on %s", acl_group)
                            return True
    logger.debug("Task forbidden")
    return False

def list_tasks(config: dict, options: dict):
    """
    Function listing tasks available to the user limited to given infra/stage/task
    """
    task_list = []
    for item in config["tasks"]["tasks"]:
        task_list.append(item["name"])

    print("  ".join(task_list))

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

def get_all_user_groups():
    """
    Function returning all user groups in form of their names
    """
    user_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
    logger.debug("User groups:%s %s", user_groups, grp.getgrgid(os.getgid()).gr_name)
    user_groups.append(str(grp.getgrgid(os.getgid()).gr_name))


    return user_groups

def load_global_configuration(conf_dir):
    """Function responsible for single file loading and validation"""
    main_config_file = os.path.join(conf_dir, "ansible-deploy.yaml")
    check_cfg_permissions_and_owner(main_config_file)
    with open(main_config_file, "r", encoding="utf8") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
            return config
        except yaml.YAMLError as e:
            logger.critical(e, file=sys.stderr)
            sys.exit(51)

def get_tags_for_task(config: dict, options: dict):
    """Function to get task's tags"""
    tags = []
    for task in config["tasks"]["tasks"]:
        if task["name"] == options["task"]:
            tags = task.get("tags", [])

    return tags

def main():
    """ansible-deploy endpoint function"""
    global logger, conf

    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if len(sys.argv) < 2:
        print("[CRITICAL]: Too few arguments", file=sys.stderr)
        sys.exit(2)
    options = parse_options(sys.argv[1:])
    logger = set_logging(options)

    conf_dir = APP_CONF
    if options["conf_dir"]:
        conf_dir = options["conf_dir"]

    conf = load_global_configuration(conf_dir)
    if options["subcommand"] in ("run", "verify"):
        workdir = create_workdir(start_ts)
        set_logging_to_file(workdir, start_ts)

    validate_options(options)
    config = load_configuration(conf_dir)
    selected_items = validate_option_values_against_config(config, options)

    user_groups = get_all_user_groups()

    if options["dry"]:
        logger.info("Skipping execution because of --dry-run option")
        sys.exit(0)

    if options["subcommand"] == "list":
        list_tasks(config, options)
    else:
        lockdir = os.path.join(conf["global_paths"]["work_dir"], "locks")
        inv_file = get_inventory_file(config, options)
        lockpath = os.path.join(lockdir, inv_file.lstrip(f".{os.sep}").replace(os.sep, "_"))
        if options["subcommand"] in ("run", "verify"):
            if not verify_task_permissions(selected_items, user_groups, config):
                logger.critical("Task forbidden")
                sys.exit(errno.EPERM)
            setup_ansible(config["tasks"]["setup_hooks"], options["commit"], workdir)
            lock_inventory(lockdir, lockpath)
            run_playitem(config, options, inv_file, lockpath)
            unlock_inventory(lockpath)
        elif options["subcommand"] == "lock":
            lock_inventory(lockdir, lockpath)
        elif options["subcommand"] == "unlock":
            unlock_inventory(lockpath)

    sys.exit(0)
