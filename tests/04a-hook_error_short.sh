#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                   _                 _                                     _                _\n  / _ \| || |   __ _          | |__   ___   ___ | | __   ___ _ __ _ __ ___  _ __   ___| |__   ___  _ __| |_\n | | | | || |_ / _\` |  _____  | '_ \ / _ \ / _ \| |/ /  / _ \ '__| '__/ _ \| '__| / __| '_ \ / _ \| '__| __|\n | |_| |__   _| (_| | |_____| | | | | (_) | (_) |   <  |  __/ |  | | | (_) | |    \__ \ | | | (_) | |  | |_\n  \___/   |_|  \__,_|         |_| |_|\___/ \___/|_|\_\  \___|_|  |_|  \___/|_|    |___/_| |_|\___/|_|   \__|\n"
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[ERROR\]: /etc/ansible-deployer/hooks/error_hook.sh: line 3: dos2uni: command not found'
check_run_ok 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' 
