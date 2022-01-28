#!/bin/bash -l

check_output() {
	CMD=$1
	EXPTEXT=$2

	eval "$CMD |& grep '$EXPTEXT'" 
	if [ $? -eq 0 ]
	then
		echo "OK: '${CMD} returned ${EXPTEXT}'"
	else
		echo "FAILED: '${CMD}' didn't return '${EXPTEXT}'"
		exit 1
	fi
}

#Check wrong combinations
check_output 'ansible-deploy' '\[ERROR\]: To fee arguments'
check_output 'ansible-deploy run' '\[ERROR\]: task is required for run'
check_output 'ansible-deploy run' '\[ERROR\]: infra is required for run'
check_output 'ansible-deploy run' '\[ERROR\]: stage is required for run'
check_output 'ansible-deploy run  -t testTask' '\[ERROR\]: stage is required for run'
check_output 'ansible-deploy run  -t testTask' '\[ERROR\]: infra is required for run'
check_output 'ansible-deploy run  -t testTask -i testInfra' 'stage is required for run'

check_output 'ansible-deploy lock -t testTask -i testInfra' '\[ERROR\]: task is not supported by lock'
check_output 'ansible-deploy lock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by lock'
check_output 'ansible-deploy lock -t testTask -s prod' '\[ERROR\]: infra is required for lock'
check_output 'ansible-deploy lock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by lock'

check_output 'ansible-deploy unlock -t testTask -i testInfra' '\[ERROR\]: task is not supported by unlock'
check_output 'ansible-deploy unlock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by unlock'
check_output 'ansible-deploy unlock -t testTask -s test' '\[ERROR\]: infra is required for unlock'
check_output 'ansible-deploy unlock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by unlock'

check_output 'ansible-deploy list --commit testTask'  '\[ERROR\]: commit is not supported by list'

#Check if correct combinations are accepted
ansible-deploy run -t run_bin_true -s prod -i test1
ansible-deploy run -t run_bin_true -s prod -i test1 --commit test_version
ansible-deploy lock -s prod -i test1
ansible-deploy unlock -s prod -i test1
ansible-deploy list
ansible-deploy list --task="run_bin_true"
