"""Sqlite database schema dictionaries"""

SCHEMAS = {
    "sequences": {
        "sequence_id": "text",
        "hostname": "text",
        "user_id": "text",
        "hooks": "text",
        "task": "text",
        "start": "text",
        "end": "text",
        "host_locked": "text",
        "keep_locked_on": "text",
        "self_setup_on": "text",
        "conf_dir_on": "text"
    },
    "play_item_tasks": {
        "task_id": "integer primary key autoincrement",
        "sequence_id": "text",
        "task_name": "text",
        "result": "text",
        "hostname": "text",
        "timestamp": "text",
        "task_details": "text"
    }
}
