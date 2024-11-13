"""Global variables"""

APP_CONF = "/etc/ansible-deployer"
CFG_PERMISSIONS = "0o644"
SUBCOMMANDS = ("run", "lock", "unlock", "verify", "show")
PRINT_FAIL = '\033[91m'
PRINT_END = '\033[0m'
OPTION_EXPANSION = {
    "infra": "infrastructure",
    "raw_output": "raw_runner_output",
    "conf_val": "conf_validation"
}
ANSIBLE_DEFAULT_CALLBACK_PLUGIN_PATH = '~/.ansible/plugins/callback:/usr/share/ansible/plugins/' \
                                       'callback'
SUPPORTED_STDOUT_CALLBACK_PLUGINS = ["yaml"]
REQUIRED_CALLBACK_PLUGINS = ["log_plays_adjusted", "sqlite_deployer"]
SUPPORTED_CALLBACK_PLUGINS = ["log_plays_adjusted", "sqlite_deployer"]
