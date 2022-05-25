#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                   _                 _\n  / _ \| || |   __ _          | |__   ___   ___ | | __   ___ _ __ _ __ ___  _ __\n | | | | || |_ / _\` |  _____  | '_ \ / _ \ / _ \| |/ /  / _ \ '__| '__/ _ \| '__|\n | |_| |__   _| (_| | |_____| | | | | (_) | (_) |   <  |  __/ |  | | | (_) | |\n  \___/   |_|  \__,_|         |_| |_|\___/ \___/|_|\_\  \___|_|  |_|  \___/|_|\n"
check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[ERROR\]: /etc/ansible-deployer/hooks/error_hook.sh: line 3: dos2uni: command not found'
check_run_ok 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra'
