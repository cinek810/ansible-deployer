#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n                               _\n   ___ ___  _ __ _ __ ___  ___| |_    _____  _____  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / _ \ \/ / _ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  |  __/>  <  __/ (__\n  \___\___/|_|  |_|  \___|\___|\__|  \___/_/\_\___|\___|\n"
# Correct execution.
check_run_ok "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra -l testHost1 --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer run -t tagged_task_true -s testing -i testInfra --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer verify -t task_exec_bin_true -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir"

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n  _                 _ _     _               _   _\n (_)_ ____   ____ _| (_) __| |   ___  _ __ | |_(_) ___  _ __  ___\n | | '_ \ \ / / _\` | | |/ _\` |  / _ \| '_ \| __| |/ _ \| '_ \/ __|\n | | | | \ V / (_| | | | (_| | | (_) | |_) | |_| | (_) | | | \__ \ \n |_|_| |_|\_/ \__,_|_|_|\__,_|  \___/| .__/ \__|_|\___/|_| |_|___/\n                                     |_|\n"
# Non-existent option values
check_message_in_output "ansible-deployer run -t task_exec_bin_ERR -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: task_exec_bin_ERR not found in configuration file."
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra_ERR --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: testInfra_ERR not found in configuration file."
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod_ERR -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: prod_ERR not found in configuration file."

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n      _    _             _\n  ___| | _(_)_ __  _ __ (_)_ __   __ _\n / __| |/ / | '_ \| '_ \| | '_ \ / _\` |\n \__ \   <| | |_) | |_) | | | | | (_| |\n |___/_|\_\_| .__/| .__/|_|_| |_|\__, |\n            |_|   |_|            |___/\n"
# Check infra/stage skipping
## Sometimes skip (depending on stage)
check_message_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[INFO\]: Skipping playitem"
check_message_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir" "ran succesfully"
## Always skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra2 --conf-dir=/etc/alternate-deployer-dir" "ran succesfully"
## Never skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra3 --conf-dir=/etc/alternate-deployer-dir" "\[INFO\]: Skipping playitem"

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n                                _ _\n   ___ ___  _ __ ___  _ __ ___ (_) |_ ___\n  / __/ _ \| '_ \` _ \| '_ \` _ \| | __/ __|\n | (_| (_) | | | | | | | | | | | | |_\__ \ \n  \___\___/|_| |_| |_|_| |_| |_|_|\__|___/\n"
# Check --commit option
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v1.1 --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.4 --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.5.1 --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v3.6.5 --conf-dir=/etc/alternate-deployer-dir"
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v1.0.1 --conf-dir=/etc/alternate-deployer-dir" "\[ERROR\]: Requested commit tags/v1.0.1 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.1 --conf-dir=/etc/alternate-deployer-dir" "\[ERROR\]: Requested commit tags/v2.1 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v3.6.6 --conf-dir=/etc/alternate-deployer-dir" "\[ERROR\]: Requested commit tags/v3.6.6 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer verify -t task_exec_bin_true -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir" "1 passed"

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n        _   _\n   ___ | |_| |__   ___ _ __ ___\n  / _ \| __| '_ \ / _ \ '__/ __|\n | (_) | |_| | | |  __/ |  \__ \ \n  \___/ \__|_| |_|\___|_|  |___/\n"
# Miscellaneous
check_message_in_output "ansible-deployer run -t task_empty -s testing -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: No playitems found for requested task"
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[INFO\]: setup_work_dir finished succesfully"

# Artificially generate lock
check_run_ok "ansible-deployer unlock -s locked -i testInfra --conf-dir=/etc/alternate-deployer-dir"
check_run_ok "ansible-deployer lock -s locked -i testInfra --conf-dir=/etc/alternate-deployer-dir"
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s locked -i testInfra --conf-dir=/etc/alternate-deployer-dir" "is using this infrastructure, please try again later."

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n  _ _           _ _                 _   _\n | (_)_ __ ___ (_) |_    ___  _ __ | |_(_) ___  _ __\n | | | '_ \` _ \| | __|  / _ \| '_ \| __| |/ _ \| '_ \ \n | | | | | | | | | |_  | (_) | |_) | |_| | (_) | | | |\n |_|_|_| |_| |_|_|\__|  \___/| .__/ \__|_|\___/|_| |_|\n                             |_|\n"
# Check --limit option
check_message_in_output "ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHost4 --conf-dir=/etc/alternate-deployer-dir" "ERROR\! Specified hosts and/or --limit does not match any hosts"
check_message_in_output "ansible-deployer run -t task_without_limit -s testing -i testInfra -l testHost1 --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: Limit testHost1 is not available for task task_without_limit."
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra -l testHost1 --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: Limit testHost1 is not available for task task_exec_bin_true."
## Multiple hosts in limit
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHosts --conf-dir=/etc/alternate-deployer-dir"

# Check if deployer exits on 1st play item fail
check_message_in_output "ansible-deployer run -t task_with_ansible_fail -s testing -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[ERROR\]: \"ansible-playbook -v -i ./test_infra1_inv.yaml runll.yaml\" failed due to"
check_message_not_in_output "ansible-deployer run -t task_with_ansible_fail -s testing -i testInfra --conf-dir=/etc/alternate-deployer-dir" "\[INFO\]: \"ansible-playbook -v -i ./test_infra1_inv.yaml runBinTrue.yaml\" ran succesfully"

echo -e "   ___ ____  _                    _               _                                _ _   _                        __       _ _            _                _\n  / _ \___ \| |__             ___| |__   ___  ___| | ___ __ _   _ _ __   __      _(_) |_| |__     ___ ___  _ __  / _|   __| (_)_ __   ___| |__   ___  _ __| |_\n | | | |__) | '_ \   _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \  \ \ /\ / / | __| '_ \   / __/ _ \| '_ \| |_   / _\` | | '__| / __| '_ \ / _ \| '__| __|\n | |_| / __/| |_) | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |  \ V  V /| | |_| | | | | (_| (_) | | | |  _| | (_| | | |    \__ \ | | | (_) | |  | |_\n  \___/_____|_.__/           \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|   \_/\_/ |_|\__|_| |_|  \___\___/|_| |_|_|    \__,_|_|_|    |___/_| |_|\___/|_|   \__|\n \n                            _         _\n  _ __   ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __  ___\n | '_ \ / _ \ '__| '_ \` _ \| / __/ __| |/ _ \| '_ \/ __|\n | |_) |  __/ |  | | | | | | \__ \__ \ | (_) | | | \__ \ \n | .__/ \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|___/\n |_|\n"
# Try execution of task without permissions
if [ $UID -ne 0 ]
then
	check_message_in_output "ansible-deployer run -t root_only_task -i testInfra -s testing --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: Task forbidden"
else
	check_message_in_output "ansible-deployer run -t non_root_task -i testInfra -s testing --conf-dir=/etc/alternate-deployer-dir" "\[CRITICAL\]: Task forbidden"
fi

