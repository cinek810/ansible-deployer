#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[CRITICAL\]: Setup hook exit_hook failed, cannot continue'
