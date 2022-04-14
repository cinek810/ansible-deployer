"""Miscellaneous helper functions"""

import os
import sys
import grp


def create_workdir(timestamp: str, conf: dict, logger):
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

    if not options["switches"]:
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
