#!/usr/bin/python

import sys
import os

VERSION = "0.1"

def run():
    sys.argv.insert(1, "serve")
    if len(sys.argv) <= 2:
        # set default file
        config_file_path = os.path.join(os.getcwd(), "config.py")
        sys.argv.append(config_file_path)
    from pecan.commands import CommandRunner
    CommandRunner.handle_command_line()
