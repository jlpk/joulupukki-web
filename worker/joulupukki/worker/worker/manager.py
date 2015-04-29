import os
import logging

import pecan

import time
from threading import Thread

from joulupukki.worker.worker.builder import Builder
from joulupukki.worker.worker.docker_builder import DockerBuilder
from joulupukki.worker.worker.osx_builder import OsxBuilder
from joulupukki.common.datamodel.build import Build
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.user import User


from joulupukki.common.logger import get_logger_path, get_logger
from joulupukki.common.carrier import Carrier


class Manager(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.must_run = False
        self.app = app
        self.build_list = {}
        self.carrier = Carrier(
            pecan.conf.rabbit_server,
            pecan.conf.rabbit_port,
            pecan.conf.rabbit_user,
            pecan.conf.rabbit_password,
            pecan.conf.rabbit_vhost,
            pecan.conf.rabbit_db
        )
        self.supported_build_type = pecan.conf.supported_build_type
        for build_type in self.supported_build_type:
            self.carrier.declare_queue('%s.queue' % build_type)

        self.logger = None

    def shutdown(self):
        logging.debug("Stopping Manager")
        self.carrier.closing = True
        self.must_run = False

    def run(self):
        self.must_run = True
        logging.debug("Starting Manager")

        while self.must_run:
            time.sleep(0.1)
            for build_type in self.supported_build_type:
                new_build = self.carrier.get_message('%s.queue' % build_type)

                build = None
                if new_build is not None:
                    distro_name = new_build['distro_name']
                    build_conf = new_build['build_conf']
                    root_folder = new_build['root_folder']
                    build = Build(new_build['build'])
                    path = os.path.dirname(get_logger_path(build))
                    os.makedirs(path)
                    self.logger = get_logger(build, distro_name)
                    self.logger.debug(build.dumps())
                    self.logger.debug("test")
                    builder_class = globals().get(build_type.title() + 'Builder')
                    builder = builder_class(distro_name, build_conf, root_folder, self.logger, build)
                    builder.run()
                    """
                    build = Build(new_build)
                    build.user = User.fetch(new_build['username'],
                                            sub_objects=False)
                    build.project = Project.fetch(build.user,
                                                  new_build['project_name'],
                                                  sub_objects=False)
                    """
                """if build:
                    logging.debug("Task received")
                    builder = Builder(build)
                    self.build_list[builder.uuid2] = builder
                    builder.start()
                """
