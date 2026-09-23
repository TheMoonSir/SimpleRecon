#!/usr/bin/env python3

import os
import shutil
import stat
import sys

source = "main.py"
rename = "srecon"
local_destination = os.path.expanduser("~/.local/bin/srecon")
system_destination = "/usr/bin/srecon"


def main():
    if os.geteuid() != 0:
        print("you need to run with sudo for building the tool.")
        sys.exit(1)

    if not os.path.exists(source):
        print(f"oops.. {source} not found")
        sys.exit(1)

    if os.path.exists(rename):
        os.remove(rename)

    os.rename(source, rename)

    os.chmod(
        rename,
        os.stat(rename).st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH,
    )
	
    os.makedirs(os.path.dirname(local_destination), exist_ok=True)

    if os.path.exists(local_destination):
        os.remove(local_destination)
		
    shutil.copy2(rename, local_destination)
	
    print(f"installed to {local_destination}")

    if os.path.exists(system_destination):
        os.remove(system_destination)

    shutil.copy2(rename, system_destination)
	
    os.chmod(
            system_destination,
            os.stat(system_destination).st_mode
            | stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH,
    )

    print(f"installed to {system_destination}")

    print("build finished")


if __name__ == "__main__":
    main()