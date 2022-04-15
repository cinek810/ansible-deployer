"""Module for configuration files handling"""

import os
import sys
import stat
import yaml
from cerberus import Validator
from ansible_deployer.modules.globalvars import APP_CONF, CFG_PERMISSIONS
from ansible_deployer.modules.configs.schema import SCHEMAS


class Config:
    """Class handling global configuration, and other configs: tasks, infrastructures,
    permissions"""

    def __init__(self, logger, conf_dir):
        self.logger = logger
        self.conf_dir = conf_dir if conf_dir else APP_CONF
        self.conf = self.load_global_configuration()

    def load_configuration_file(self, config_path: str):
        """Function responsible for single file loading and validation"""
        #TODO: Add verification of owner/group/persmissions
        if config_path == APP_CONF:
            self.check_cfg_permissions_and_owner(config_path)
        config_file = os.path.basename(config_path)
        self.logger.debug("Loading :%s", config_file)

        with open(config_path, "r", encoding="utf8") as config_stream:
            try:
                config = yaml.safe_load(config_stream)
            except yaml.YAMLError as e:
                self.logger.critical("Yaml loading failed for %s due to %s.", config_path, e)
                sys.exit(51)

        schema_name = config_file.split(".")[0]
        validator = Validator(SCHEMAS[schema_name])
        if not validator.validate(config, SCHEMAS[schema_name]):
            self.logger.critical("Yaml validation failed for %s due to %s.", config_path,
                                 validator.errors)
            sys.exit(53)

        self.logger.debug("Loaded:\n%s", str(config))
        return config

    def check_cfg_permissions_and_owner(self, cfg_path: str):
        """Function to verify permissions and owner for config files"""
        stat_info = os.stat(cfg_path)

        if stat_info.st_uid == 0:
            if oct(stat.S_IMODE(stat_info.st_mode)) == CFG_PERMISSIONS:
                self.logger.debug("Correct permissions and owner for config file %s.", cfg_path)
            else:
                self.logger.error("File %s permissions are incorrect! Contact your sys admin.",
                                  cfg_path)
                self.logger.error("Program will exit now.")
                sys.exit(40)
        else:
            self.logger.error("File %s owner is not root! Contact your sys admin.", cfg_path)
            self.logger.error("Program will exit now.")
            sys.exit(41)

    def get_config_paths(self):
        """Function to create absolute config paths and check their extension compatibility"""
        ymls = []
        yamls = []
        infra_cfg = None
        tasks_cfg = None
        acl_cfg = None

        for config in os.listdir(self.conf_dir):
            if config != "ansible-deploy.yaml":
                if config.endswith(".yml"):
                    ymls.append(config)
                elif config.endswith(".yaml"):
                    yamls.append(config)

                if config.startswith("infra"):
                    infra_cfg = os.path.join(self.conf_dir, config)
                elif config.startswith("tasks"):
                    tasks_cfg = os.path.join(self.conf_dir, config)
                elif config.startswith("acl"):
                    acl_cfg = os.path.join(self.conf_dir, config)

        if len(ymls) > 0 and len(yamls) > 0:
            self.logger.debug("Config files with yml extensions: %s", " ".join(ymls))
            self.logger.debug("Config files with yaml extensions: %s", " ".join(yamls))
            self.logger.critical("Config files with different extensions (.yml and .yaml) are not"
                                 " allowed in conf dir %s !", self.conf_dir)
            sys.exit(42)

        if not infra_cfg:
            self.logger.critical("Infrastructure configuration file infra.yaml does not exist in"
                                 " %s!", self.conf_dir)
            sys.exit(43)

        if not tasks_cfg:
            self.logger.critical("Tasks configuration file tasks.yaml does not exist in %s!",
                                 self.conf_dir)
            sys.exit(44)

        if not acl_cfg:
            self.logger.critical("Permission configuration file acl.yaml does not exist in %s!",
                                 self.conf_dir)
            sys.exit(45)

        return infra_cfg, tasks_cfg, acl_cfg

    def load_configuration(self):
        """Function responsible for reading configuration files and running a schema validator
        against it"""
        self.logger.debug("load_configuration called")
        #TODO: validate files/directories permissions - should be own end editable only by
        #special user
        infra_cfg, tasks_cfg, acl_cfg = self.get_config_paths()

        infra = self.load_configuration_file(infra_cfg)
        tasks = self.load_configuration_file(tasks_cfg)
        acl = self.load_configuration_file(acl_cfg)

        config = {}
        config["infra"] = infra["infrastructures"]
        config["tasks"] = tasks

        config["acl"] = {}
        for group in acl["acl_lists"]:
            key = group["name"]
            group.pop("name")
            config["acl"][key] = group

        return config

    def load_global_configuration(self):
        """Function responsible for single file loading and validation"""
        main_config_file = os.path.join(self.conf_dir, "ansible-deploy.yaml")
        if self.conf_dir == APP_CONF:
            self.check_cfg_permissions_and_owner(main_config_file)
        with open(main_config_file, "r", encoding="utf8") as config_stream:
            try:
                config = yaml.safe_load(config_stream)
                return config
            except yaml.YAMLError as e:
                self.logger.critical(e, file=sys.stderr)
                sys.exit(51)
