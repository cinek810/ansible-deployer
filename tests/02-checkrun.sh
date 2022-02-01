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

#Check wrong combinations
check_run_ok "ansible-deploy run -t task_exec_bin_true -s prod -i testInfra"

