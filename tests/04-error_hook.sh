#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[ERROR\]: /etc/ansible-deploy/hooks/error_hook.sh: line 3: dos2uni: command not found'
check_run_ok 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' 
