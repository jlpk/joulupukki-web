import os

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
        self.logger.debug("TESTTTTTTT")
        """steps = (('setup', self.setup),
                 ('preparing', self.parse_s
        """

    def parse_specdeb(self):
        pass
