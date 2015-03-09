
import logging


import pecan

import time
from threading import Thread

from joulupukki.worker.worker.builder import Builder

from joulupukki.common.datamodel.build import Build


from joulupukki.worker.lib.queues import build_tasks
from joulupukki.common.carrier import Carrier



class Manager(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.must_run = False
        self.app = app
        self.build_list = {}
        self.carrier = Carrier(pecan.conf.rabbit_server, pecan.conf.rabbit_port, pecan.conf.rabbit_db)

    def shutdown(self):
        logging.debug("Stopping Manager")
        self.must_run = False

    def run(self):
        self.must_run = True
        logging.debug("Starting Manager")

        while self.must_run:
            time.sleep(0.1)
            new_build = self.carrier.get_build()
            if new_build:
                logging.debug("Task received")
                new_build = Build.create(new_build.project, new_build)
                builder = Builder(new_build)
                self.build_list[builder.uuid2] = builder
                builder.start()

