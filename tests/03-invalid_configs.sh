#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ _____           _                 _ _     _                    __ _\n  / _ \___ /          (_)_ ____   ____ _| (_) __| |   ___ ___  _ __  / _(_) __ _ ___\n | | | ||_ \   _____  | | '_ \ \ / / _\` | | |/ _\` |  / __/ _ \| '_ \| |_| |/ _\` / __|\n | |_| |__) | |_____| | | | | \ V / (_| | | | (_| | | (_| (_) | | | |  _| | (_| \__ \ \n  \___/____/          |_|_| |_|\_/ \__,_|_|_|\__,_|  \___\___/|_| |_|_| |_|\__, |___/\n                                                                           |___/\n"
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra" "\[CRITICAL\]: Config files with different extensions (.yml and .yaml) are not allowed in conf dir"

