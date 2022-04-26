#!/bin/bash -l


source ./tests/testing_lib.sh

check_message_in_output 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra' '\[CRITICAL\]: Config files with different extensions (.yml and .yaml) are not allowed in conf dir'

