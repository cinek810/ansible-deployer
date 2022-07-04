"""Setuptools configuration for ansible-deployer"""
import pathlib
import os
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


def read(fname):
    """Helper function for README"""
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='UTF-8').read()

README = read(str(HERE)+"/README.md")


# This call to setup() does all the work
setup(
    name="ansible-deployer",
    version="0.0.34",
    description="Wrapper around ansible-playbook allowing configurable tasks and permissions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cinek810/ansible-deployer",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.9"
    ],
    package_dir={"ansible_deployer": "source"},
    packages=[
    "ansible_deployer",
    "ansible_deployer.modules",
    "ansible_deployer.modules.configs",
    "ansible_deployer.modules.outputs",
    "ansible_deployer.modules.locking",
    "ansible_deployer.modules.runners",
    "ansible_deployer.modules.validators"
    ],
    include_package_data=True,
    install_requires=["pyyaml>=5.3.1", "cerberus>=1.3.1", "pytest-testinfra>=6.6.0"],
    entry_points={
        "console_scripts": [
            "ansible-deployer = ansible_deployer.main:main",
        ]
    },
)
