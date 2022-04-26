#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[CRITICAL\]: Setup hook exit_hook failed, cannot continue'
