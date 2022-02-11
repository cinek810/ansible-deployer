#!/bin/bash -l

check_message_in_output() {
        CMD=$1
        EXPTEXT=$2
        echo "Check: $CMD"
        eval "$CMD |& grep '$EXPTEXT'"
        if [ $? -eq 0 ]
        then
                echo "OK: '${CMD}' returned '${EXPTEXT}'"
        else
                echo "FAILED: '${CMD}' didn't return '${EXPTEXT}'"
                exit 1
        fi
}

check_message_not_in_output() {
        CMD=$1
        EXPTEXT=$2
        echo "Check: $CMD"
        eval "$CMD |& grep '$EXPTEXT'"
        if [ $? -eq 0 ]
        then
                echo "FAILED: '${CMD}' returned '${EXPTEXT}'"
                exit 1
        else
                echo "OK: '${CMD}' didn't return '${EXPTEXT}'"
        fi
}

check_run_ok() {
	CMD=$1
	echo "Check: $CMD"
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
check_run_ok "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra"
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra -l testHost1"
check_run_ok "ansible-deployer run -t tagged_task_true -s testing -i testInfra"
# # multiple hosts in limit
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHosts"

# Non-existent option values
check_message_in_output 'ansible-deployer run -t task_exec_bin_ERR -s prod -i testInfra' '\[ERROR\]: task_exec_bin_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra_ERR' '\[ERROR\]: testInfra_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod_ERR -i testInfra' '\[ERROR\]: prod_ERR not found in configuration file.'

# misc
check_message_in_output 'ansible-deployer run -t task_empty -s testing -i testInfra' '\[ERROR\]: No playbooks found for requested task'

#Artificially generate lock
check_run_ok "ansible-deployer lock -s locked -i testInfra"
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s locked -i testInfra' "is using this infrastructure, please try again later."

#Check --debug option
check_run_ok "ansible-deployer list --debug" "\[DEBUG\]: load_configuration called"

# Check --limit option
check_message_in_output 'ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHost4' 'ERROR\! Specified hosts and/or --limit does not match any hosts'

#Try execution of task without permissions
if [ $UID -ne 0 ]
then
	check_message_in_output "ansible-deployer run -t root_only_task -i testInfra -s testing" "\[ERROR\]: Task forbidden"
else
	check_message_in_output "ansible-deployer run -t non_root_task -i testInfra -s testing" "\[ERROR\]: Task forbidden"
fi
