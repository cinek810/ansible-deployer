#!/bin/bash

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

