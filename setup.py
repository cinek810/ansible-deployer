"""Setuptools configuration for ansible-deploy"""
import pathlib
import os
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
#README = (HERE / "README.md").read_text()


def read(fname):
    """Helper function for README"""
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='UTF-8').read()

README = read(str(HERE)+"/README.md")

# This call to setup() does all the work
setup(
    name="ansible-deploy",
    version="0.0.4",
    description="Wrapper around ansible-playbook allowing configurable tasks and permissions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cinek810/ansible-deploy",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.9"
    ],
    packages=["ansible_deploy"],
    include_package_data=True,
    install_requires=["pyyaml", "cerberus"],
    entry_points={
        "console_scripts": [
            "ansible-deploy = ansible_deploy.command_line:main",
        ]
    },
)
