
import logging


import pecan

import time
from threading import Thread

from joulupukki.worker.worker.builder import Builder
from joulupukki.common.datamodel.build import Build
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.user import User

from joulupukki.common.carrier import Carrier


class Manager(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.must_run = False
        self.app = app
        self.build_list = {}
        self.carrier = Carrier(pecan.conf.rabbit_server,
                               pecan.conf.rabbit_port, pecan.conf.rabbit_db)
        self.carrier.declare_queue('builds.queue')

    def shutdown(self):
        logging.debug("Stopping Manager")
        self.carrier.closing = True
        self.must_run = False

    def run(self):
        self.must_run = True
        logging.debug("Starting Manager")

        while self.must_run:
            time.sleep(0.1)
            new_build = self.carrier.get_message('builds.queue')
            build = None
            if new_build is not None:
                build = Build(new_build)
                build.user = User.fetch(new_build['username'],
                                        sub_objects=False)
                build.project = Project.fetch(build.user,
                                              new_build['project_name'],
                                              sub_objects=False)

            if build:
                logging.debug("Task received")
                builder = Builder(build)
                self.build_list[builder.uuid2] = builder
                builder.start()
