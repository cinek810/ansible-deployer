#!/bin/bash -l


source ./tests/testing_lib.sh

#Check wrong combinations
check_message_in_output 'ansible-deployer' 'Too few arguments'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: task is required for run'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: infra is required for run'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: stage is required for run'
check_message_in_output 'ansible-deployer run  -t testTask' '\[ERROR\]: stage is required for run'
check_message_in_output 'ansible-deployer run  -t testTask' '\[ERROR\]: infra is required for run'
check_message_in_output 'ansible-deployer run  -t testTask -i testInfra' 'stage is required for run'

check_message_in_output 'ansible-deployer lock -t testTask -i testInfra' '\[ERROR\]: task is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -s prod' '\[ERROR\]: infra is required for lock'
check_message_in_output 'ansible-deployer lock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -l test_hosts_1' '\[ERROR\]: limit is not supported by lock'

check_message_in_output 'ansible-deployer unlock -t testTask -i testInfra' '\[ERROR\]: task is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -s test' '\[ERROR\]: infra is required for unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -l test_hosts_1' '\[ERROR\]: limit is not supported by unlock'

check_message_in_output 'ansible-deployer list --commit testTask'  '\[ERROR\]: commit is not supported by list'
check_message_in_output 'ansible-deployer list -l test_hosts_1'  '\[ERROR\]: limit is not supported by list'

#Check if correct combinations are accepted
check_run_ok "ansible-deployer run --dry -t task_exec_bin_true -s prod -i testInfra"
check_run_ok "ansible-deployer run --dry -t task_with_limit -s testing -i testInfra -l testHost1"
check_run_ok "ansible-deployer run --dry -t task_exec_bin_true -s prod -i testInfra --commit test_version"
check_run_ok "ansible-deployer lock --dry -s prod -i testInfra"
check_run_ok "ansible-deployer unlock --dry -s prod -i testInfra"
check_run_ok "ansible-deployer list"
check_run_ok "ansible-deployer list --task=task_exec_bin_true"

#Check if wrong config is rejected
check_message_in_output 'ansible-deployer run --dry -t task_exec_bin_true -i nonExistingInfra -s prod' '\[ERROR\]: nonExistingInfra not found in configuration file'
