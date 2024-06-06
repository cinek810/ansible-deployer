"""Miscellaneous helper functions"""

import os
import sys
import grp


def create_parent_workdir(short_ts: str, date_dir: str, conf: dict, logger):
    """Function to create parent working directory"""
    if short_ts not in os.listdir(conf["global_paths"]["work_dir"]):
        try:
            os.mkdir(date_dir)
            try:
                os.chmod(date_dir, int(conf["permissions"]["parent_workdir"], 8))
                logger.debug("Successfully created parent work dir: %s", date_dir)
            except Exception as exc:
                logger.critical("Failed to change permissions of parent work dir: %s error was: %s",
                                date_dir, exc)
                sys.exit(90)
        except Exception as exc:
            logger.critical("Failed to create parent work dir: %s error was: %s", date_dir, exc)
            sys.exit(90)

def create_workdir(timestamp: str, conf: dict, logger):
    """
    Function to create working directory on file system, we expect it to change
    the cwd to newly created workdir at the end.
    """
    short_ts = timestamp.split("_")[0]
    date_dir = os.path.join(conf["global_paths"]["work_dir"], short_ts)
    base_dir = os.path.join(date_dir, conf["global_paths"]["sequences_subdir"])
    create_parent_workdir(short_ts, date_dir, conf, logger)

    #
    #TODO: Add locking of the directory
    if conf["global_paths"]["sequences_subdir"] not in os.listdir(date_dir):
        seq_path = os.path.join(base_dir, f"{conf['file_naming']['sequence_prefix']}0000")
        try:
            os.mkdir(base_dir)
            try:
                os.chmod(base_dir, int(conf["permissions"]["parent_workdir"], 8))
                logger.debug("Successfully created parent work dir: %s", base_dir)
            except Exception as exc:
                logger.critical("Failed to change permissions of parent work dir: %s error was: %s",
                                base_dir, exc)
                sys.exit(90)
        except Exception as exc:
            logger.critical("Failed to create parent work dir: %s error was: %s", base_dir, exc)
            sys.exit(90)
    else:
        sequence_list = os.listdir(base_dir)
        sequence_list.sort()
        new_sequence = int(sequence_list[-1].split(conf['file_naming']['sequence_prefix'])[1]) + 1
        seq_path = os.path.join(base_dir, f"{conf['file_naming']['sequence_prefix']}"
                                          f"{new_sequence:04d}")

    try:
        os.mkdir(seq_path)
        os.chmod(seq_path, int(conf["permissions"]["workdir"], 8))
    except Exception as e:
        logger.critical("Failed to create work dir: %s error was: %s", seq_path, e, file=sys.stderr)
        sys.exit(91)
    logger.debug("Successfully created workdir: %s", seq_path)
    return seq_path

# TODO: At least infra level should be returned from validate options since we do similar check
# (existence) there.
def get_inventory_file(config: dict, options: dict, logger):
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

    if not inv_file:
        if options["inventory"]:
            inv_file = options["inventory"]
            logger.debug(f"Using specified inventory file: {inv_file} .")
        else:
            logger.critical("No inventory loaded.")
    elif options["inventory"]:
        logger.info('Ignoring specified inventory file: {options["inventory"]} . Using the'\
                    ' configured one: {inv_file} .')
    else:
        logger.debug(f"Using configured inventory file: {inv_file} .")

    return inv_file

def get_all_user_groups(logger):
    """
    Function returning all user groups in form of their names
    """
    user_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
    logger.debug("User groups:%s %s", user_groups, grp.getgrgid(os.getgid()).gr_name)
    user_groups.append(str(grp.getgrgid(os.getgid()).gr_name))


    return user_groups

def show_deployer(config: dict, options: dict):
    """
    Function showing available configs: tasks, infrastructures, permissions.
    """
    content = {}

    if not options["switches"] or "all" in options["switches"]:
        options["switches"] = ["task", "infra"]

    if "task" in options["switches"]:
        content["tasks"] = []
        for item in config["tasks"]["tasks"]:
            content["tasks"].append(item["name"])

    if "infra" in options["switches"]:
        content["infrastructures"] = []
        for item in config["infra"]:
            content["infrastructures"].append(item["name"])

    print(format_show_deployer(content))

def format_show_deployer(print_data: dict):
    """
    Format data from show_deployer function to output
    """
    content = ""
    for key, value in print_data.items():
        values = ", ".join(value).strip(", ")
        content = f"{content}\n\nAvailable {key}:\n{values}\n"

    return content
