import time
import json
import os

import pecan
import wsme
import wsme.types as wtypes

from joulupukki.controllers.v2.datamodel import types
from joulupukki.controllers.v2.datamodel.user import User
from joulupukki.controllers.v2.datamodel.project import Project
from joulupukki.controllers.v2.datamodel.build import Build
from joulupukki.lib.distros import supported_distros, reverse_supported_distros



source_types = wtypes.Enum(str, 'local', 'git')

class APIJob(types.Base):
    pass

class Job(APIJob):
    id_ = wsme.wsattr(int, mandatory=False)
    created = wsme.wsattr(float, mandatory=False)
    distro = wsme.wsattr(wtypes.text, mandatory=False)
    status = wsme.wsattr(wtypes.text, mandatory=False)
    root_folder = wsme.wsattr(wtypes.text, mandatory=False)
    # TODO guess which user is...
    user = wsme.wsattr(User, mandatory=False)
    project = wsme.wsattr(Project, mandatory=False)
    build = wsme.wsattr(Build, mandatory=False)

    @classmethod
    def sample(cls):
        # TODO
        return cls(
            source_url="https://github.com/kaji-project/shinken.git",
            source_type="git",
            branch="master",
        )


    @staticmethod
    def get_folder_path(username, project_name, build_id, id_):
        """ Return job folder path"""
        return os.path.join(pecan.conf.workspace_path,
                            username,
                            project_name,
                            "builds",
                            str(build_id),
                            "jobs",
                            str(id_))

    @staticmethod
    def get_data_file_path(username, project_name, build_id, id_):
        """ Return build data file (build.cfg) path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name, "builds", str(build_id), "jobs", str(id_), "job.cfg")


    def get_folder_output(self):
        folder_path = Build.get_folder_path(self.user.username,
                                            self.project.name,
                                            self.build.id_)
        return os.path.join(folder_path, "output", reverse_supported_distros.get(self.distro, "bad_distro_name"))

    def get_log(self):
        log_file = os.path.join(pecan.conf.workspace_path, self.user.username, self.project.name, "builds", str(self.build.id_), "jobs", str(self.id_), "log.txt")
        # Read status_file
        with open(log_file, 'r') as f:
            try:
                log = f.read()
            except Exception as exp:
                return
        return log



    @classmethod
    def fetch(cls, build, id_, full_data=True):
        job_folder_path = Job.get_folder_path(build.user.username, build.project.name, build.id_, id_)
        if not os.path.isdir(job_folder_path):
            # User doesn't exists
            return None
        job_file = Job.get_data_file_path(build.user.username, build.project.name, build.id_, id_)
        if not os.path.isfile(job_file):
            # config not found ...
            # this is release strange
            # this environnement is in bad state
            # we should think about delete it
            return False
        # Read userdata.cfg
        with open(job_file, 'r') as f:
            try:
                job_data = json.load(f)
                job = cls(**job_data)
                if full_data:
                    job.project = build.project
                    job.user = build.user
                    job.build = build
                return job
            except Exception as exp:
                # TODO handle error
                return False


    @classmethod
    def create(cls, build, job_data):
        if not isinstance(job_data, dict):
            job_dict = job_data.as_dict()
        else:
            job_dict = job_data
        latest_job = build.get_latest_job()
        job_dict['id_'] = 1
        if latest_job is not None:
            job_dict['id_'] = int(latest_job) + 1
        job_dict['user'] = build.user
        job_dict['project'] = build.project
        job_dict['build'] = build
        job_dict['status'] = "created"
        job_dict['created'] = time.time()

        # Create folder
        job = cls(**job_dict)
        os.makedirs(Job.get_folder_path(build.user.username, build.project.name, build.id_, job_dict['id_']))
        job.save()
        return job


    def save(self):
        job_file = Job.get_data_file_path(self.user.username, self.project.name, self.build.id_, self.id_)
        distro = reverse_supported_distros.get(self.distro, self.distro)
        data = json.dumps({
                           "id_": self.id_,
                           "created": self.created,
                           "distro": distro,
                           "status": self.status,
                           })

        with open(job_file, 'w') as f:
            try:
                f.write(data)
            except Exception as exp:
                # TODO handle error
                raise Exception("Error saving job data")
        return True


    def set_status(self, status):
        self.status = status
        self.save()
