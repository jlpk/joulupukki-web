from threading import Thread
import glob
import os
import shutil

import pecan
import git
import yaml

from joulupukki.common.distros import supported_distros, distro_templates
from joulupukki.common.logger import get_logger, get_logger_docker, get_logger_job
from joulupukki.common.datamodel.job import Job

import json




from docker import Client
import re

import time

import urlparse
from joulupukki.common.carrier import Carrier


class Logger(Thread):
    def __init__(self):
        Thread.__init__(self, name="logger")
        self.must_run = None
        self.carrier = Carrier(pecan.conf.rabbit_server, pecan.conf.rabbit_port, pecan.conf.rabbit_db)
        self.carrier.declare_logs()
        self.carrier.subscribe_logs()

        # Create docker client
        # Set folders
#        self.folder = build.get_folder_path()
#        self.folder_source = build.get_source_folder_path()
        # Create folders
#        if not os.path.exists(self.folder):
#            os.makedirs(self.folder)
#        if not os.path.isdir(self.folder):
        # TODO handle error
#            raise Exception("%s should be a folder" % folder)
        # Prepare logger
#        self.logger = get_logger(self)


    def run(self):
        self.must_run = True
        while self.must_run:
            log = self.carrier.get_log()
            if log is not None:
                self.write_log(log)
                
            else:
                time.sleep(0.1)
        


    def shutdown(self):
        self.must_run = False


    def write_log(self, log):
#        print log
        # TODO
        # We have to check if log file is already there
        # Because we don't want a partial log file...
        # Get job object
        job = Job(log['job'])
        folder_output = job.get_folder_output()
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
        job_tmp_folder = job.get_folder_tmp()
        if not os.path.exists(job_tmp_folder):
            os.makedirs(job_tmp_folder)
        # Get logger
        logger = get_logger_job(job)
        # Write log
        if 'args' in log and log['args']:
            getattr(logger, log['level'])(log['log'], log['args'][0])
        else:
            getattr(logger, log['level'])(log['log'])
        # Remove handler 
        logger.removeHandler(logger.handlers[0])
