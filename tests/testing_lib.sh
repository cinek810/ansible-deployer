#!/bin/bash

check_run_ok() {
        CMD=$1
        echo "Check: $CMD"
        $CMD
        if [ $? -ne 0 ]
        then
                echo "FAILED: ${CMD}"
		echo "$CMD"
		eval "$CMD"
                exit 1
        else
                echo "OK"
        fi
}

check_run_fail() {
        CMD=$1
        echo "Check: $CMD"
        $CMD
        if [ $? -eq 0 ]
        then
		echo "FAILED(Expected failure got return code of 0): ${CMD}"
		echo "$CMD"
		eval "$CMD"
                exit 1
        else
                echo "OK - failed as expected"
        fi
}


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
		echo $CMD
		eval $CMD
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
		echo $CMD
		eval $CMD
                exit 1
        else
                echo "OK: '${CMD}' didn't return '${EXPTEXT}'"
        fi
}

check_file_permissions() {
	filemode=$(stat -c '%a' $1)
	if [ $filemode -eq $2 ]
	then
		echo "OK: $1 has correct permissions $2"
	else
		echo "FAILED: $1 has incorrect permissions $2"
	fi
}

find_latest_sequence() {
	last_seq="$(ls /tmp/$(date +%Y%m%d) | tail -n 1)"
	echo "/tmp/$(date +%Y%m%d)/${last_seq}"
}

check_file_startingwith_in_dir() {
	eval "find $1 -name "${2}*" 1>/dev/null"
	if [ $? -eq 0 ]
	then
		echo "OK: $1 has file starting with pattern $2"
	else
		echo "FAILED: $1 does not contain file starting with pattern $2"
		exit 1
	fi
}

check_message_with_newline_in_output() {
        CMD=$1
        EXPTEXT=$2
        echo "Check: $CMD"
        eval "$CMD |& grep -zP '$EXPTEXT'"
        if [ $? -eq 0 ]
        then
                echo "OK: '${CMD}' returned '${EXPTEXT}'"
        else
                echo "FAILED: '${CMD}' didn't return '${EXPTEXT}'"
		echo $CMD
		eval $CMD
                exit 1
        fi
}
