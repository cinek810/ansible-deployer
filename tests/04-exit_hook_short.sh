#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _  _                       _ _     _                 _\n  / _ \| || |             _____  _(_) |_  | |__   ___   ___ | | __\n | | | | || |_   _____   / _ \ \/ / | __| | '_ \ / _ \ / _ \| |/ /\n | |_| |__   _| |_____| |  __/>  <| | |_  | | | | (_) | (_) |   <\n  \___/   |_|            \___/_/\_\_|\__| |_| |_|\___/ \___/|_|\_\ \n"
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[CRITICAL\]: Setup hook exit_hook failed, cannot continue'
