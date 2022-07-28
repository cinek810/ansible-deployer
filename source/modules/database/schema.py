"""Sqlite database schema dictionaries"""

SCHEMAS = {
    "sequences": {
        "sequence_id": "",
        "hostname": "",
        "user_id": "",
        "hooks": "",
        "task": "",
        "start": "",
        "end": "",
        "host_locked": "",
        "keep_locked_on": "",
        "self_setup_on": "",
        "conf_dir_on": ""
    },
    "play_item_tasks": {
        "sequence_id": "",
        "task_name": "",
        "hostname": "",
        "cmd": "",
        "start": "",
        "end": "",
        "delta": "",
        "rc": "",
        "msg": "",
        "stderr": "",
        "stderr_lines": "",
        "stdout": "",
        "stdout_lines": ""
    }
}
