#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ _____           _                 _ _     _                    __ _                 _                _\n  / _ \___ /          (_)_ ____   ____ _| (_) __| |   ___ ___  _ __  / _(_) __ _ ___   ___| |__   ___  _ __| |_\n | | | ||_ \   _____  | | '_ \ \ / / _\` | | |/ _\` |  / __/ _ \| '_ \| |_| |/ _\` / __| / __| '_ \ / _ \| '__| __|\n | |_| |__) | |_____| | | | | \ V / (_| | | | (_| | | (_| (_) | | | |  _| | (_| \__ \ \__ \ | | | (_) | |  | |_\n  \___/____/          |_|_| |_|\_/ \__,_|_|_|\__,_|  \___\___/|_| |_|_| |_|\__, |___/ |___/_| |_|\___/|_|   \__|\n                                                                           |___/\n"
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra" "\[CRITICAL\]: Config files with different extensions (.yml and .yaml) are not allowed in conf dir"

