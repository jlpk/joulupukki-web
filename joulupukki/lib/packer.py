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
from joulupukki.lib.logger import get_logger, get_logger_docker


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

        self.config = config
        self.source_url = builder.source_url
        self.source_type = builder.source_type
        self.cli = builder.cli
        self.set_status_builder = builder.set_status
        self.builder = builder

        self.folder_output_tmp = os.path.join(builder.folder,
                                              self.config['distro'],
                                              'tmp')
        self.folder_output = os.path.join(builder.folder,
                                          self.config['distro'],
                                          'output'
                                          )
        if not os.path.exists(self.folder_output):
            os.makedirs(self.folder_output)
        if not os.path.exists(self.folder_output_tmp):
            os.makedirs(self.folder_output_tmp)

        self.logger = get_logger_docker(builder.uuid, config['distro'])

        self.folder = builder.folder


        self.container_tag = "joulupukki"
        self.container = None


    def set_status(self, status):
        self.set_status_builder(status, self.config['distro'])

    def run(self):
        steps = (('preparing', self.parse_specdeb),
                 ('building', self.docker_build),
                 ('packaging', self.docker_run),
                 ('finishing', self.get_output),
                 ('cleaning', self.clean_up),
                 )

        for step_name, step_function in steps:
            self.set_status(step_name)
            if step_function() is not True:
                self.logger.debug("Task failed during step: %s", step_name)
                self.set_status('failed')
                return False
            # Save package name in build.cfg 
            if self.config.get('name') is not None and self.builder.package_name is None:
                self.builder.package_name = self.config.get('name')
                self.builder.save_to_disk()
            if self.config.get('version') is not None and self.builder.package_version is None:
                self.builder.package_version = self.config.get('version')
                self.builder.save_to_disk()
            if self.config.get('release') is not None and self.builder.package_release is None:
                self.builder.package_release = self.config.get('release')
                self.builder.save_to_disk()
        self.set_status('succeeded')
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
