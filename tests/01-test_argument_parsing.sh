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

check_output 'ansible-deploy' '\[ERROR\]: To fee arguments'
check_output 'ansible-deploy run' '\[ERROR\]: run requires --task'

