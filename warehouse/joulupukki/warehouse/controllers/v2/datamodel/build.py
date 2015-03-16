import time
import json
import os

import pecan
import wsme
import wsme.types as wtypes

from joulupukki.web.controllers.v2.datamodel import types
from joulupukki.web.controllers.v2.datamodel.user import User
from joulupukki.web.controllers.v2.datamodel.project import Project
from joulupukki.web.lib.distros import supported_distros


source_types = wtypes.Enum(str, 'local', 'git')

class APIBuild(types.Base):
    source_url = wsme.wsattr(wtypes.text, mandatory=True)
    source_type = wsme.wsattr(source_types, mandatory=True, default="git")
    commit = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    branch = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    forced_distro = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    snapshot = wsme.wsattr(bool, mandatory=False, default=False)

class Build(APIBuild):
    id_ = wsme.wsattr(int, mandatory=False)
    created = wsme.wsattr(float, mandatory=False, default=None)
    package_name = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    package_version = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    package_release = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    status = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    # TODO guess which user is...
    user = wsme.wsattr(User, mandatory=False)
    project = wsme.wsattr(Project, mandatory=False)
    jobs = wsme.wsattr([wtypes.text], mandatory=False, default=None)

    @classmethod
    def sample(cls):
        return cls(
            source_url="https://github.com/kaji-project/shinken.git",
            source_type="git",
            branch="master",
        )


    def dumps(self):
        dump = self.as_dict()
        dump['user'] = self.user.dumps()
        dump['project'] = self.project.dumps()
        return dump


    @staticmethod
    def get_folder_path(username, project_name, id_):
        """ Return build folder path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name, "builds", str(id_))

    @staticmethod
    def get_data_file_path(username, project_name, id_):
        """ Return build data file (build.cfg) path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name, "builds", str(id_), "build.cfg")

    def get_source_folder_path(self):
        """ Return project folder path"""
        return os.path.join(pecan.conf.workspace_path,
                            self.__class__.get_folder_path(self.user.username, self.project.name, self.id_),
                            "sources")

    def get_output_folder_path(self, distro=None):
        """ Return project folder path"""
        if distro not in supported_distros:
            return os.path.join(pecan.conf.workspace_path,
                                self.__class__.get_folder_path(self.user.username, self.project.name, self.id_),
                                "output")
        else:
            return os.path.join(pecan.conf.workspace_path,
                            self.__class__.get_folder_path(self.user.username, self.project.name, self.id_),
                            "output",
                            distro)

    @classmethod
    def fetch(cls, project, id_, sub_objects=True, full_data=False):
        build_folder_path = Build.get_folder_path(project.user.username, project.name, id_)
        if not os.path.isdir(build_folder_path):
            # User doesn't exists
            return None
        build_file = Build.get_data_file_path(project.user.username, project.name, id_)
        if not os.path.isfile(build_file):
            # config not found ...
            # this is release strange
            # this environnement is in bad state
            # we should think about delete it
            return False
        # Read userdata.cfg
        with open(build_file, 'r') as f:
            try:
                build_data = json.load(f)
                build = cls(**build_data)
                if sub_objects or full_data:
                    build.project = project
                    build.user = project.user
                    build.jobs = build.get_jobs()
                    if not full_data:
                        build.user = None
                        build.project = None
                    
                return build
            except Exception as exp:
                # TODO handle error
                return False



    @classmethod
    def create(cls, project, build_data):
        build_dict = build_data.as_dict()
        latest_build = project.get_latest_build()
        build_dict['id_'] = 1
        if latest_build is not None:
            build_dict['id_'] = int(latest_build) + 1
        build_dict['user'] = project.user
        build_dict['project'] = project
        build_dict['created'] = time.time()
        build_dict['status'] = "created"

        # Create folder
        build = cls(**build_dict)
        os.makedirs(Build.get_folder_path(project.user.username, project.name, build_dict['id_']))
        build.save()
        build.jobs = build.get_jobs()
        return build


    def save(self):
        build_file = Build.get_data_file_path(self.user.username, self.project.name, self.id_)
        data = json.dumps({"source_url": self.source_url,
                           "source_type": self.source_type,
                           "branch": self.branch,
                           "commit": self.commit,
                           "id_": self.id_,
                           "created": self.created,
                           "package_name": self.package_name,
                           "package_version": self.package_version,
                           "package_release": self.package_release,
                           "status": self.status,
                           })

        with open(build_file, 'w') as f:
            try:
                f.write(data)
            except Exception as exp:
                # TODO handle error
                raise Exception("Error saving build data")
        return True


    def get_jobs(self):
        """ return all build ids """
        build_path = self.__class__.get_folder_path(self.user.username, self.project.name, self.id_)
        jobs_path = os.path.join(build_path, "jobs")
        if not os.path.isdir(jobs_path):
            return []
        jobs_ids = []
        for id_ in os.listdir(jobs_path):
            try:
                jobs_ids.append(id_)
            except ValueError:
                continue
        return sorted(jobs_ids, key=lambda x: int(x))

    def get_latest_job(self):
        job_ids = self.get_jobs()
        if job_ids == []:
            return None
        return job_ids[-1]


    def set_status(self, status):
        self.status = status
        self.save()

