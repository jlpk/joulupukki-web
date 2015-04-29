import os
import subprocess

from joulupukki.worker.lib.packer import Packer
from joulupukki.common.logger import get_logger, get_logger_job
from joulupukki.common.datamodel.job import Job

class OsxPacker(object):
    def __init__(self, builder, config):
        self.config = config
        self.builder = builder
        self.distro = "osx"
        
        self.source_url = builder.source_url
        self.source_type = builder.source_type
        self.folder = builder.folder

        job_data = {
            'distro': self.distro,
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

        self.logger = get_logger_job(self.job)

    def set_status(self, status):
        self.job.set_status(status)

    def set_build_time(self, build_time):
        self.job.set_build_time(build_time)

    def run(self):
        steps = (
            ('setup', self.setup),
            ('compiling', self.compile_),
        )
        for step_name, step_function in steps:
            self.set_status(step_name)
            if step_function() is not True:
                self.logger.debug("Task failed during step: %s", step_name)
                self.set_status('failed')
                return False
            # Save package name in build.cfg
            if (self.config.get('name') is not None and
                    self.builder.build.package_name is None):
                self.builder.build.package_name = self.config.get('name')
                self.builder.build._save()
        self.set_status('succeeded')
        return True

    def setup(self):
        cmd = "brew install automake libtool gettext yasm autoconf pkg-config qt5"
        cmd_list = cmd.split(" ")
        # Installing dependencies
        process = subprocess.Popen(
            ["brew", "install", "automake", "libtool", "gettext",
             "yasm", "autoconf", "pkg-config", "qt5"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.logger.debug(stdout)
        self.logger.error(stderr)
        if process:
            return False
        return True

    def compile_(self):
        # Compiling ring-daemon
        os.system("git clone git@git.savoirfairelinux.com:ring-daemon.git")
        os.system("cd ring-daemon/contrib")
        os.system("mkdir native")
        os.system("cd native")
        os.system("../bootstrap")
        os.system("make -j3")

    def parse_specdeb(self):
        pass
