"""Sqlite database schema dictionaries"""

SCHEMAS = {
    "sequences": {
        "sequence_id": "varchar",
        "hostname": "varchar",
        "user_id": "varchar",
        "hooks": "varchar",
        "task": "varchar",
        "start": "datetime",
        "end": "datetime",
        "host_locked": "boolean",
        "keep_locked_on": "boolean",
        "self_setup_on": "boolean",
        "conf_dir_on": "boolean"
    },
    "play_item_tasks": {
        "sequence_id": "varchar",
        "task_name": "varchar",
        "hostname": "varchar",
        "task_details": "json"
    }
}
