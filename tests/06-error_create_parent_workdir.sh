#!/bin/bash -l


source ./tests/testing_lib.sh

ls -ld /tmp/workdir
ansible-deployer run -t task_exec_bin_true -s prod -i testInfra -d

check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[CRITICAL\]: Failed to create parent work dir'
