#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____                     _               _                                _ _   _                _  __            _                     _                _\n  / _ \___ \ ___            ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__    ___  ___| |/ _|  ___  ___| |_ _   _ _ __    ___| |__   ___  _ __| |_\n | | | |__) / __|  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \  / __|/ _ \ | |_  / __|/ _ \ __| | | | '_ \  / __| '_ \ / _ \| '__| __|\n | |_| / __/ (__  |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | \__ \  __/ |  _| \__ \  __/ |_| |_| | |_) | \__ \ | | | (_) | |  | |_\n  \___/_____\___|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_| |___/\___|_|_|   |___/\___|\__|\__,_| .__/  |___/_| |_|\___/|_|   \__|\n                                                                                                                                  |_|\n  _            _\n | |_ __ _ ___| | __\n | __/ _\` / __| |/ /\n | || (_| \__ \   <\n  \__\__,_|___/_|\_\ \n"
# Check if cwd is correctly switched when using --self-setup option
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_not_in_output "ansible-deployer run -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
echo -e "   ___ ____                     _               _                                _ _   _                _  __            _                     _                _\n  / _ \___ \ ___            ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__    ___  ___| |/ _|  ___  ___| |_ _   _ _ __    ___| |__   ___  _ __| |_\n | | | |__) / __|  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \  / __|/ _ \ | |_  / __|/ _ \ __| | | | '_ \  / __| '_ \ / _ \| '__| __|\n | |_| / __/ (__  |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | \__ \  __/ |  _| \__ \  __/ |_| |_| | |_) | \__ \ | | | (_) | |  | |_\n  \___/_____\___|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_| |___/\___|_|_|   |___/\___|\__|\__,_| .__/  |___/_| |_|\___/|_|   \__|\n                                                                                                                                  |_|\n                 _  __\n __   _____ _ __(_)/ _|_   _\n \ \ / / _ \ '__| | |_| | | |\n  \ V /  __/ |  | |  _| |_| |\n   \_/ \___|_|  |_|_|  \__, |\n                       |___/\n"
check_message_in_output "ansible-deployer verify -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[DEBUG\]: Successfully created workdir: /tmp/"
check_message_not_in_output "ansible-deployer verify -t task_exec_bin_true -s testing -i testInfra -d --self-setup /etc/alt-workdir" "\[INFO\]: Setup completed in /etc/alt-workdir"
search_path=$(find_latest_sequence)
check_file_startingwith_in_dir "/etc/alt-workdir" "runBin.yaml"
check_file_startingwith_in_dir "$search_path" "ansible-deploy_execution_"
