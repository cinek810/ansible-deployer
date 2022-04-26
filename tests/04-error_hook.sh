#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[ERROR\]: /etc/ansible-deployer/hooks/error_hook.sh: line 3: dos2uni: command not found'
check_run_ok 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra'
