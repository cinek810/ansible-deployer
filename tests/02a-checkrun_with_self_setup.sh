#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n           _ _   _                _  __            _\n __      _(_) |_| |__    ___  ___| |/ _|  ___  ___| |_ _   _ _ __\n \ \ /\ / / | __| '_ \  / __|/ _ \ | |_  / __|/ _ \ __| | | | '_ \ \n  \ V  V /| | |_| | | | \__ \  __/ |  _| \__ \  __/ |_| |_| | |_) |\n   \_/\_/ |_|\__|_| |_| |___/\___|_|_|   |___/\___|\__|\__,_| .__/\n                                                            |_|\n"
# Check if cwd is correctly switched when using --self-setup option
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage testing --infrastructure testInfra --debug --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_not_in_output "ansible-deployer run --task task_exec_bin_true --stage testing --infrastructure testInfra --debug --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
check_message_in_output "ansible-deployer verify --task task_exec_bin_true --stage testing --infrastructure testInfra --debug --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_not_in_output "ansible-deployer verify --task task_exec_bin_true --stage testing --infrastructure testInfra --debug --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
