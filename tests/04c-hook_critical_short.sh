#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                  _                 _                _ _   _           _       _                _\n  / _ \| || |   ___          | |__   ___   ___ | | __   ___ _ __(_) |_(_) ___ __ _| |  ___| |__   ___  _ __| |_\n | | | | || |_ / __|  _____  | '_ \ / _ \ / _ \| |/ /  / __| '__| | __| |/ __/ _\` | | / __| '_ \ / _ \| '__| __|\n | |_| |__   _| (__  |_____| | | | | (_) | (_) |   <  | (__| |  | | |_| | (_| (_| | | \__ \ | | | (_) | |  | |_\n  \___/   |_|  \___|         |_| |_|\___/ \___/|_|\_\  \___|_|  |_|\__|_|\___\__,_|_| |___/_| |_|\___/|_|   \__|\n"
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[CRITICAL\]: Failed executing /etc/ansible-deployer/hooks/exit_hook.sh'
