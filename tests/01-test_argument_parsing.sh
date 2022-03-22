#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                                                       _     _             _   _\n __      ___ __ ___  _ __   __ _    ___ ___  _ __ ___ | |__ (_)_ __   __ _| |_(_) ___  _ __  ___\n \ \ /\ / / '__/ _ \| '_ \ / _\` |  / __/ _ \| '_ \` _ \| '_ \| | '_ \ / _\` | __| |/ _ \| '_ \/ __|\n  \ V  V /| | | (_) | | | | (_| | | (_| (_) | | | | | | |_) | | | | | (_| | |_| | (_) | | | \__ \\n   \_/\_/ |_|  \___/|_| |_|\__, |  \___\___/|_| |_| |_|_.__/|_|_| |_|\__,_|\__|_|\___/|_| |_|___/\n                           |___/\n \n"
#Check wrong combinations
check_message_in_output 'ansible-deployer' '\[CRITICAL\]: Too few arguments'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: task is required for run'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: infra is required for run'
check_message_in_output 'ansible-deployer run' '\[ERROR\]: stage is required for run'
check_message_in_output 'ansible-deployer run  -t testTask' '\[ERROR\]: stage is required for run'
check_message_in_output 'ansible-deployer run  -t testTask' '\[ERROR\]: infra is required for run'
check_message_in_output 'ansible-deployer run  -t testTask -i testInfra' 'stage is required for run'

check_message_in_output 'ansible-deployer lock -t testTask -i testInfra' '\[ERROR\]: task is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -s prod' '\[ERROR\]: infra is required for lock'
check_message_in_output 'ansible-deployer lock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by lock'
check_message_in_output 'ansible-deployer lock -t testTask -l test_hosts_1' '\[ERROR\]: limit is not supported by lock'

check_message_in_output 'ansible-deployer unlock -t testTask -i testInfra' '\[ERROR\]: task is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -i testInfra -s prod' '\[ERROR\]: task is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -s test' '\[ERROR\]: infra is required for unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -s prod -c X' '\[ERROR\]: commit is not supported by unlock'
check_message_in_output 'ansible-deployer unlock -t testTask -l test_hosts_1' '\[ERROR\]: limit is not supported by unlock'

check_message_in_output 'ansible-deployer list --commit testTask'  '\[ERROR\]: commit is not supported by list'
check_message_in_output 'ansible-deployer list -l test_hosts_1'  '\[ERROR\]: limit is not supported by list'

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                               _                         _     _             _   _\n   ___ ___  _ __ _ __ ___  ___| |_    ___ ___  _ __ ___ | |__ (_)_ __   __ _| |_(_) ___  _ __  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / __/ _ \| '_ \` _ \| '_ \| | '_ \ / _\` | __| |/ _ \| '_ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  | (_| (_) | | | | | | |_) | | | | | (_| | |_| | (_) | | | \__ \\n  \___\___/|_|  |_|  \___|\___|\__|  \___\___/|_| |_| |_|_.__/|_|_| |_|\__,_|\__|_|\___/|_| |_|___/\n \n"
#Check if correct combinations are accepted
check_run_ok "ansible-deployer run --dry -t task_exec_bin_true -s prod -i testInfra"
check_run_ok "ansible-deployer run --dry -t task_with_limit -s testing -i testInfra -l testHost1"
check_run_ok "ansible-deployer run --dry -t task_exec_bin_true -s prod -i testInfra --commit test_version"
check_run_ok "ansible-deployer lock --dry -s prod -i testInfra"
check_run_ok "ansible-deployer unlock --dry -s prod -i testInfra"
check_run_ok "ansible-deployer list"
check_run_ok "ansible-deployer list --task=task_exec_bin_true"

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                                                    __ _\n __      ___ __ ___  _ __   __ _    ___ ___  _ __  / _(_) __ _\n \ \ /\ / / '__/ _ \| '_ \ / _\` |  / __/ _ \| '_ \| |_| |/ _\` |\n  \ V  V /| | | (_) | | | | (_| | | (_| (_) | | | |  _| | (_| |\n   \_/\_/ |_|  \___/|_| |_|\__, |  \___\___/|_| |_|_| |_|\__, |\n                           |___/                         |___/\n \n"
#Check if wrong config is rejected
check_message_in_output 'ansible-deployer run --dry -t task_exec_bin_true -i nonExistingInfra -s prod' '\[CRITICAL\]: nonExistingInfra not found in configuration file'
