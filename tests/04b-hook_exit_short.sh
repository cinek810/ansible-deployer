#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _   _               _                 _                _ _         _                _\n  / _ \| || | | |__           | |__   ___   ___ | | __   _____  _(_) |_   ___| |__   ___  _ __| |_\n | | | | || |_| '_ \   _____  | '_ \ / _ \ / _ \| |/ /  / _ \ \/ / | __| / __| '_ \ / _ \| '__| __|\n | |_| |__   _| |_) | |_____| | | | | (_) | (_) |   <  |  __/>  <| | |_  \__ \ | | | (_) | |  | |_\n  \___/   |_| |_.__/          |_| |_|\___/ \___/|_|\_\  \___/_/\_\_|\__| |___/_| |_|\___/|_|   \__|\n"
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra" "\[CRITICAL\]: Setup hook exit_hook failed, cannot continue"
