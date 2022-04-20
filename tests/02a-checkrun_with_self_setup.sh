#!/bin/bash -l


source ./tests/testing_lib.sh

# Check if cwd is correctly switched when using --self-setup option
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
check_message_in_output "ansible-deployer verify --task=task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_in_output "ansible-deployer verify --task=task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
