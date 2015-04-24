#!/usr/bin/python
import os
import logging
import shutil
import time
from datetime import datetime

from threading import Thread

from joulupukki.common.logger import get_logger, get_logger_docker
from joulupukki.common.distros import reverse_supported_distros, supported_distros
from joulupukki.common.datamodel.job import Job


"""
created
setup
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
        import ipdb;ipdb.set_trace()
        self.distro = supported_distros[config['distro']]
        self.source_url = builder.source_url
        self.source_type = builder.source_type
        self.cli = builder.cli
        self.builder = builder
        self.folder = builder.folder

        job_data = {
            'distro': config['distro'],
            'username': self.builder.build.username,
            'project_name': self.builder.build.project_name,
            'build_id': self.builder.build.id_,
        }
        self.job = Job(job_data)
        self.job.create()
        self.folder_output = self.job.get_folder_output()

        self.job_tmp_folder = self.job.get_folder_tmp()

        if not os.path.exists(self.folder_output):
            os.makedirs(self.folder_output)
        if not os.path.exists(self.job_tmp_folder):
            os.makedirs(self.job_tmp_folder)

        self.logger = get_logger_docker(self.job)

        self.container_tag = "joulupukki:" + config['distro'].replace(":", "_")
        self.container = None

    def set_status(self, status):
        self.job.set_status(status)

    def set_build_time(self, build_time):
        self.job.set_build_time(build_time)

    def run(self):
        steps = (('setup', self.setup),
                 ('preparing', self.parse_specdeb),
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
            if self.config.get('name') is not None and self.builder.build.package_name is None:
                self.builder.build.package_name = self.config.get('name')
                self.builder.build._save()
            if self.config.get('version') is not None and self.builder.build.package_version is None:
                self.builder.build.package_version = self.config.get('version')
                self.builder.build._save()
            if self.config.get('release') is not None and self.builder.build.package_release is None:
                self.builder.build.package_release = self.config.get('release')
                self.builder.build._save()
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

    def setup(self):
        # Remove images
        for image in self.cli.images():
            if not any([True for tag in image['RepoTags'] if tag.startswith("joulupukki:")]):
                continue
            try:
                creation_date = datetime.fromtimestamp(image.get('Created'))
                delta_time = datetime.now() - creation_date
                if delta_time.days >= 1:
                    self.logger.debug('Deleting docker image: %s', image['Id'])
                    self.cli.remove_image(image['Id'])
            except Exception as error:
                self.logger.debug('Cannot deleting docker image: %s'
                                  ' - Error: %s', image['Id'], error)
        return True

    def clean_up(self):
        # Set end time
        self.job.set_end_time(time.time())
        # Delete container
        self.logger.debug('Deleting docker container: %s', self.container['Id'])
        self.cli.remove_container(self.container['Id'])
        if os.path.isdir(self.job_tmp_folder):
            shutil.rmtree(self.job_tmp_folder)


        return True
