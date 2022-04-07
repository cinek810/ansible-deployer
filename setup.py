"""Setuptools configuration for ansible-deployer"""
import pathlib
import os
from setuptools import setup
from ansible_deployer import version

#sys.path.append("/home/runner/work/ansible-deployer/ansible-deployer")

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
    version=version.__version__,
    description="Wrapper around ansible-playbook allowing configurable tasks and permissions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cinek810/ansible-deployer",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.9"
    ],
    packages=["ansible_deployer"],
    include_package_data=True,
    install_requires=["pyyaml>=5.3.1", "cerberus>=1.3.1", "pytest-testinfra>=6.6.0"],
    entry_points={
        "console_scripts": [
            "ansible-deployer = ansible_deployer.command_line:main",
        ]
    },
)
