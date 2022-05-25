#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                                        _                 _\n  / _ \| || |             ___ _ __ _ __ ___  _ __  | |__   ___   ___ | | __\n | | | | || |_   _____   / _ \ '__| '__/ _ \| '__| | '_ \ / _ \ / _ \| |/ /\n | |_| |__   _| |_____| |  __/ |  | | | (_) | |    | | | | (_) | (_) |   <\n  \___/   |_|            \___|_|  |_|  \___/|_|    |_| |_|\___/ \___/|_|\_\ \n"
check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[ERROR\]: /etc/ansible-deployer/hooks/error_hook.sh: line 3: dos2uni: command not found'
check_run_ok 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra'
