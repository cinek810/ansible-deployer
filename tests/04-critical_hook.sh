#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                       _ _   _           _   _                 _\n  / _ \| || |             ___ _ __(_) |_(_) ___ __ _| | | |__   ___   ___ | | __\n | | | | || |_   _____   / __| '__| | __| |/ __/ _\` | | | '_ \ / _ \ / _ \| |/ /\n | |_| |__   _| |_____| | (__| |  | | |_| | (_| (_| | | | | | | (_) | (_) |   <\n  \___/   |_|            \___|_|  |_|\__|_|\___\__,_|_| |_| |_|\___/ \___/|_|\_\ \n"
check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[CRITICAL\]: Failed executing /etc/ansible-deployer/hooks/exit_hook.sh'
