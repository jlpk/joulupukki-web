#!/usr/bin/python

import sys
import os

VERSION = "0.1"

def run():
    from pecan.commands import CommandRunner
    sys.argv.insert(1, "serve")
    if len(sys.argv) <= 2:
        # set default file
        config_file_path = os.path.join(os.getcwd(), "config.py")
        sys.argv.append(config_file_path)
    CommandRunner.handle_command_line()
