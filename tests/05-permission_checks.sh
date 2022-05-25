#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  ____                                      _         _                    _               _\n  / _ \| ___|           _ __   ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __     ___| |__   ___  ___| | _____\n | | | |___ \   _____  | '_ \ / _ \ '__| '_ \` _ \| / __/ __| |/ _ \| '_ \   / __| '_ \ / _ \/ __| |/ / __|\n | |_| |___) | |_____| | |_) |  __/ |  | | | | | | \__ \__ \ | (_) | | | | | (__| | | |  __/ (__|   <\__ \ \n  \___/|____/          | .__/ \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|  \___|_| |_|\___|\___|_|\_\___/\n                       |_|\n"
check_run_ok 'ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra'

check_file_permissions "/tmp/$(date +%Y%m%d)" 1750
