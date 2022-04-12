#!/bin/bash -l

dos2uni /etc/ansible-deployer/ansible-deploy.yaml
ls -l /etc/ansible-deployer/ansible-deploy.yaml

exit 1
