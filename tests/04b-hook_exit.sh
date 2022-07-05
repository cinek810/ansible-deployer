#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _   _               _                 _                _ _\n  / _ \| || | | |__           | |__   ___   ___ | | __   _____  _(_) |_\n | | | | || |_| '_ \   _____  | '_ \ / _ \ / _ \| |/ /  / _ \ \/ / | __|\n | |_| |__   _| |_) | |_____| | | | | (_) | (_) |   <  |  __/>  <| | |_\n  \___/   |_| |_.__/          |_| |_|\___/ \___/|_|\_\  \___/_/\_\_|\__|\n"
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra" "\[CRITICAL\]: Setup hook exit_hook failed, cannot continue"
