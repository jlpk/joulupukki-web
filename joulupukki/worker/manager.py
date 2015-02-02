
import logging



import time
from threading import Thread

from joulupukki.worker.builder import Builder


from joulupukki.lib.queues import build_tasks



class Manager(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.must_run = False
        self.app = app
        self.build_list = {}

    def shutdown(self):
        logging.debug("Stopping Manager")
        self.must_run = False

    def run(self):
        self.must_run = True
        logging.debug("Starting Manager")

        while self.must_run:
            time.sleep(0.1)
            if not build_tasks.empty():
                logging.debug("Task received")
                build_task = build_tasks.get()
                builder = Builder(build_task)
                self.build_list[builder.uuid] = builder
                builder.start()
                build_tasks.task_done()

