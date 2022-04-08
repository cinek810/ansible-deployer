#!/bin/bash -l

source ./tests/testing_lib.sh

check_run_ok "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra -f ./tests/files/private_cfg"
