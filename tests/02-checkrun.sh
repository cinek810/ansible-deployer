#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n                               _\n   ___ ___  _ __ _ __ ___  ___| |_    _____  _____  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / _ \ \/ / _ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  |  __/>  <  __/ (__\n  \___\___/|_|  |_|  \___|\___|\__|  \___/_/\_\___|\___|\n \n"
# Correct execution.
check_run_ok "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra"
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra -l testHost1"
check_run_ok "ansible-deployer run -t tagged_task_true -s testing -i testInfra"
check_run_ok 'ansible-deployer verify --task=task_exec_bin_true -s prod -i testInfra'
# # multiple hosts in limit
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHosts"

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n  _                 _ _     _               _   _\n (_)_ ____   ____ _| (_) __| |   ___  _ __ | |_(_) ___  _ __  ___\n | | '_ \ \ / / _\` | | |/ _\` |  / _ \| '_ \| __| |/ _ \| '_ \/ __|\n | | | | \ V / (_| | | | (_| | | (_) | |_) | |_| | (_) | | | \__ \\n |_|_| |_|\_/ \__,_|_|_|\__,_|  \___/| .__/ \__|_|\___/|_| |_|___/\n                                     |_|\n \n"
# Non-existent option values
check_message_in_output 'ansible-deployer run -t task_exec_bin_ERR -s prod -i testInfra' '\[CRITICAL\]: task_exec_bin_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra_ERR' '\[CRITICAL\]: testInfra_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod_ERR -i testInfra' '\[CRITICAL\]: prod_ERR not found in configuration file.'

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n      _    _             _\n  ___| | _(_)_ __  _ __ (_)_ __   __ _\n / __| |/ / | '_ \| '_ \| | '_ \ / _\` |\n \__ \   <| | |_) | |_) | | | | | (_| |\n |___/_|\_\_| .__/| .__/|_|_| |_|\__, |\n            |_|   |_|            |___/\n \n"
# Check infra/stage skipping
# # Sometimes skip (depending on stage)
check_message_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra" "\[INFO\]: Skipping playitem"
check_message_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra" "ran succesfully"
# # Always skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra2" "ran succesfully"# # Never skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra3" "\[INFO\]: Skipping playitem"

echo -e "  ___ ____                                     _   _\n / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n| | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n| |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n\n                               _ _\n  ___ ___  _ __ ___  _ __ ___ (_) |_ ___\n / __/ _ \| '_ \` _ \| '_ \` _ \| | __/ __|\n| (_| (_) | | | | | | | | | | | | |_\__ \ \n \___\___/|_| |_| |_|_| |_| |_|_|\__|___/\n"
# Check --commit option
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v1.1"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.4"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.5.1"
check_run_ok "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v3.6.5"
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v1.0.1" '\[ERROR\]: Requested commit tags/v1.0.1 is not valid for task task_with_commit.'
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v2.1" '\[ERROR\]: Requested commit tags/v2.1 is not valid for task task_with_commit.'
check_message_in_output "ansible-deployer run -t task_with_commit -s testing -i testInfra -c tags/v3.6.6" '\[ERROR\]: Requested commit tags/v3.6.6 is not valid for task task_with_commit.'
check_message_in_output 'ansible-deployer verify --task=task_exec_bin_true -s prod -i testInfra' '1 passed'

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n        _   _\n   ___ | |_| |__   ___ _ __ ___\n  / _ \| __| '_ \ / _ \ '__/ __|\n | (_) | |_| | | |  __/ |  \__ \\n  \___/ \__|_| |_|\___|_|  |___/\n \n"
# misc
check_message_in_output 'ansible-deployer run -t task_empty -s testing -i testInfra' '\[CRITICAL\]: No playitems found for requested task'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra' '\[INFO\]: setup_work_dir finished succesfully'

#Artificially generate lock
check_run_ok "ansible-deployer lock -s locked -i testInfra"
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s locked -i testInfra' "is using this infrastructure, please try again later."

#Check --debug option
check_run_ok "ansible-deployer list --debug" "\[DEBUG\]: load_configuration called"

# Check --limit option
check_message_in_output 'ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHost4' 'ERROR\! Specified hosts and/or --limit does not match any hosts'
check_message_in_output 'ansible-deployer run -t task_without_limit -s testing -i testInfra -l testHost1' '\[CRITICAL\]: Limit testHost1 is not available for task task_without_limit.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra -l testHost1' '\[CRITICAL\]: Limit testHost1 is not available for task task_exec_bin_true.'

# Check if deployer exits on 1st play item fail
check_message_in_output 'ansible-deployer run -t task_with_ansible_fail -s testing -i testInfra' "\[ERROR\]: \"ansible-playbook -i ./test_infra1_inv.yaml runll.yaml\" failed due to"
check_message_not_in_output 'ansible-deployer run -t task_with_ansible_fail -s testing -i testInfra' "\[INFO\]: \"ansible-playbook -i ./test_infra1_inv.yaml runBinTrue.yaml\" ran succesfully"

# Check --keep-locked option
check_message_in_output "ansible-deployer run -t task_exec_bin_true -s testing -i testInfra -k -d" "\[DEBUG\]: Keep locked infra testInfra:testing ."
check_run_ok "ansible-deployer unlock -s testing -i testInfra"

#Try execution of task without permissions
if [ $UID -ne 0 ]
then
	check_message_in_output "ansible-deployer run -t root_only_task -i testInfra -s testing" "\[CRITICAL\]: Task forbidden"
else
	check_message_in_output "ansible-deployer run -t non_root_task -i testInfra -s testing" "\[CRITICAL\]: Task forbidden"
fi

