#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re
import logging
import shutil
import glob
from urlparse import urlparse

from docker import Client

from deb_pkg_tools.control import parse_depends
from deb_pkg_tools.control import load_control_file

"""
preparing
building
packaging
finishing
cleaning
failed
succeeded
"""

class Packer(object):

    def __init__(self, builder, config):
        self.logger = builder.logger
        self.dlogger = builder.dlogger
        self.config = config
        self.git_url = builder.git_url
        self.cli = builder.cli
        self.status = builder.status

        self.folder_output_tmp = os.path.join(builder.folder,
                                              'tmp',
                                              self.config['distro'])
        self.folder_output = os.path.join(builder.folder_output,
                                          self.config['distro'])
        os.makedirs(self.folder_output)
        self.folder = builder.folder


        self.container_tag = "joulupukki"
        self.container = None

    def run(self):
        steps = (('preparing', self.parse_specdeb),
                 ('building', self.docker_build),
                 ('packaging', self.docker_run),
                 ('finishing', self.get_output),
                 ('cleaning', self.clean_up),
                 )

        for step_name, step_function in steps:
            self.status['builds'][self.config['distro']] = step_name
            if step_function() is not True:
                self.logger.debug("Task failed during step: %s", step_name)
                self.status['builds'][self.config['distro']] = 'failed'
                return False
        self.status['builds'][self.config['distro']] = 'succeeded'
        return True


    def parse_specdeb(self):
        return False

    def docker_build(self):
        return False

    def docker_run(self):
        return False

    def get_output(self):
        return False

    def clean_up(self):
        # Delete container
        self.logger.debug('Deleting docker container: %s', self.container['Id'])
        self.cli.remove_container(self.container['Id'])

        # Remove images
        for image in self.cli.images(self.container_tag):
            try:
                self.logger.debug('Deleting docker image: %s', image['Id'])
                self.cli.remove_image(image['Id'])
            except Exception as error:
                self.logger.debug('Cannot deleting docker image: %s'
                                  ' - Error: %s', image['Id'], error)
        return True
