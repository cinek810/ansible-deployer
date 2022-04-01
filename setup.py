"""Setuptools configuration for ansible-deployer"""
import pathlib
import os
import subprocess
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


def read(fname):
    """Helper function for README"""
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='UTF-8').read()

def create_bin():
    """Helper function to create binary file from source"""

    module_path = os.path.join(HERE, "ansible_deployer", "command_line.py")
    command = ["pyinstaller", "--onefile", "--name", "ansible-deployer", module_path]
    out = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print(out.stdout)
    print(out.stderr)

    bin_path = os.path.join("dist", "ansible-deployer")
    #subprocess.run(["chown", "root", bin_path], check=True)
    subprocess.run(["chmod", "4750", bin_path], check=True)

    return bin_path

README = read(str(HERE)+"/README.md")
bin_path = create_bin()

# This call to setup() does all the work
setup(
    name="ansible-deployer",
    version="0.0.18",
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
    install_requires=["pyyaml>=5.3.1", "cerberus>=1.3.4"],
    data_files = [ ("bin", [bin_path]) ]
)
