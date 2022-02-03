#!/bin/bash -l

check_output_fail() {
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

check_run_ok() {
	CMD=$1
	$CMD
	if [ $? -ne 0 ]
	then
		echo "FAILED: ${CMD}"
		exit 1
	else
		echo "OK"
	fi
}

# Correct execution.
check_run_ok "ansible-deploy run -t task_exec_bin_true -s prod -i testInfra"

# Non-existent option values
check_output_fail 'ansible-deploy run -t task_exec_bin_ERR -s prod -i testInfra' '\[ERROR\]: task_exec_bin_ERR not found in configuration file.'
check_output_fail 'ansible-deploy run -t task_exec_bin_true -s prod -i testInfra_ERR' '\[ERROR\]: testInfra_ERR not found in configuration file.'
check_output_fail 'ansible-deploy run -t task_exec_bin_true -s prod_ERR -i testInfra' '\[ERROR\]: prod_ERR not found in configuration file.'

# misc
check_output_fail 'ansible-deploy run -t task_empty -s testing -i testInfra' '\[ERROR\]: No playbooks found for requested task'

#Artificially generate lock
check_run_ok "ansible-deploy lock -s locked -i testInfra"
check_output_fail 'ansible-deploy run -t task_exec_bin_true -s locked -i testInfra' "is using this infrastructure, please try again later."

