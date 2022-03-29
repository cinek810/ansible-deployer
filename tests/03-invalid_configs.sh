#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[CRITICAL\]: Config files with different extensions (.yml and .yaml) are not allowed in conf dir'

