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
#        if not os.path.is_file(config_file_path):
#            print("%s doesn't exists" % config_file_path)
#            sys.exit(1)
        sys.argv.append("config.py")
    CommandRunner.handle_command_line()
