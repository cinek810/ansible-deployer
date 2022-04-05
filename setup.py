"""Setuptools configuration for ansible-deployer"""
from pathlib import Path
from shutil import copytree, copy
from sys import platform, exit
from os import mkdir, environ, walk, makedirs, sep
from os.path import join, split
from setuptools import setup


CFG_SOURCE = join(Path(__file__).parent, "etc")

def get_cfg_location():
    """Get destination of supplementary and config files"""
    if platform == "linux":
        location = join(environ["HOME"], ".ansible-deployer")
    else:
        print("[CRITICAL]: Your platform is not supported!")
        exit(10)

    return location

def create_cfg_location(location: str):
    """Create destination of supplementary and config files"""
    try:
        mkdir(location)
    except FileExistsError:
        print(f"[WARNING]: Config location already exists at {location}. Updating all files"
        " included.")
    except Exception as exc:
        print(f"[CRITICAL]: Unable to create config location {location} due to {exc}.")
        exit(11)

    return location

def install_configs(src_path: str, dst_path: str):
    """Copy supplementary and config files to destination"""
    try:
        copytree(src_path, dst_path)
    except FileExistsError:
        for root, _, files in walk(src_path):
            for file in files:
                print(file)
                full_path = join(root, file)
                if split(full_path)[0] == src_path:
                    copy(full_path, dst_path)
                else:
                    sub_path = join(dst_path, root.replace(src_path, "").strip(sep))
                    try:
                        makedirs(sub_path)
                        copy(full_path, sub_path)
                    except FileExistsError:
                        copy(full_path, sub_path)
                    except Exception as exc:
                        print(f"[CRITICAL]: Unable to install config file {file} due to {exc}.")
                        exit(13)
    except Exception as exc:
        print(f"[CRITICAL]: Unable to install config files due to {exc}.")
        exit(12)


if __name__ == "__main__":
    location = get_cfg_location()
    create_cfg_location(location)
    install_configs(CFG_SOURCE, location)
    setup()
