#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n                               _\n   ___ ___  _ __ _ __ ___  ___| |_    _____  _____  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / _ \ \/ / _ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  |  __/>  <  __/ (__\n  \___\___/|_|  |_|  \___|\___|\__|  \___/_/\_\___|\___|\n \n"
# Correct execution.
check_run_ok "ansible-deployer run -t task_exec_bin_true -s prod -i testInfra"
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra -l testHost1"
check_run_ok "ansible-deployer run -t tagged_task_true -s testing -i testInfra"
# # multiple hosts in limit
check_run_ok "ansible-deployer run -t task_with_limit -s testing -i testInfra2 -l xyzHosts"

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n  _                 _ _     _               _   _\n (_)_ ____   ____ _| (_) __| |   ___  _ __ | |_(_) ___  _ __  ___\n | | '_ \ \ / / _\` | | |/ _\` |  / _ \| '_ \| __| |/ _ \| '_ \/ __|\n | | | | \ V / (_| | | | (_| | | (_) | |_) | |_| | (_) | | | \__ \\n |_|_| |_|\_/ \__,_|_|_|\__,_|  \___/| .__/ \__|_|\___/|_| |_|___/\n                                     |_|\n \n"
# Non-existent option values
check_message_in_output 'ansible-deployer run -t task_exec_bin_ERR -s prod -i testInfra' '\[ERROR\]: task_exec_bin_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod -i testInfra_ERR' '\[ERROR\]: testInfra_ERR not found in configuration file.'
check_message_in_output 'ansible-deployer run -t task_exec_bin_true -s prod_ERR -i testInfra' '\[ERROR\]: prod_ERR not found in configuration file.'

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n      _    _             _\n  ___| | _(_)_ __  _ __ (_)_ __   __ _\n / __| |/ / | '_ \| '_ \| | '_ \ / _\` |\n \__ \   <| | |_) | |_) | | | | | (_| |\n |___/_|\_\_| .__/| .__/|_|_| |_|\__, |\n            |_|   |_|            |___/\n \n"
# Check infra/stage skipping
# # Sometimes skip (depending on stage)
check_message_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra" "\[INFO\]: Skipping playbook"
check_message_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra" "ran succesfully"
# # Always skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s testing -i testInfra2" "ran succesfully"# # Never skip
check_message_not_in_output "ansible-deployer run -t task_skipping -s prod -i testInfra3" "\[INFO\]: Skipping playbook"
# # unlock infra for further tests
check_run_ok "ansible-deployer unlock -s testing -i testInfra"
check_run_ok "ansible-deployer unlock -s testing -i testInfra2"

echo -e "   ___ ____                                     _   _\n  / _ \___ \            _____  _____  ___ _   _| |_(_) ___  _ __\n | | | |__) |  _____   / _ \ \/ / _ \/ __| | | | __| |/ _ \| '_ \ \n | |_| / __/  |_____| |  __/>  <  __/ (__| |_| | |_| | (_) | | | |\n  \___/_____|          \___/_/\_\___|\___|\__,_|\__|_|\___/|_| |_|\n \n        _   _\n   ___ | |_| |__   ___ _ __ ___\n  / _ \| __| '_ \ / _ \ '__/ __|\n | (_) | |_| | | |  __/ |  \__ \\n  \___/ \__|_| |_|\___|_|  |___/\n \n"
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

