import os
import re
import shutil

import pecan
import wsme
import json
import wsme.types as wtypes

from joulupukki.common.database import mongo, DESCENDING
from joulupukki.common.datamodel import types
from joulupukki.common.datamodel.build import Build


class APIProject(types.Base):
    name = wsme.wsattr(wtypes.text, mandatory=True)

class Project(APIProject):
    username = wsme.wsattr(wtypes.text, mandatory=False)
    builds = wsme.wsattr([Build], mandatory=False)

    def __init__(self, data=None, sub_objects=True):
        if data is None:
            APIProject.__init__(self)
        elif isinstance(data, APIProject):
            APIProject.__init__(self, **data.as_dict())
        else:
            APIProject.__init__(self, **data)
        if sub_objects:
            self.builds = self.get_builds()



    @classmethod
    def sample(cls):
        return cls(
            name="myproject",
        )

    def create(self):
        # Check required args
        required_args = ['name',
                        ]
        for arg in required_args:
            if not getattr(self, arg):
                # TODO handle error
                return False
        # TODO: check password
        # Write project data
        try:
            self._save()
            return True
        except Exception as exp:
            # TODO handle error
            return False

    @classmethod
    def fetch(cls, user, project_name, sub_objects=True, get_last_build=False):
        db_project = mongo.projects.find_one({"name": project_name,
                                              "username": user.username})
        project = None
        if db_project is not None:
            project = cls(db_project, sub_objects)
            if sub_objects and get_last_build:
                project.builds = [project.builds[0]]
        return project

    def _save(self):
        """ Write project data on disk """
        data = self.as_dict()
        mongo.projects.update({"name": self.name,
                               "username": data['username']},
                              data,
                              upsert=True)
        return True


    def delete(self):
        """ delete project """
        # Check password
#        if not check_password(password, self.password):
#            # TODO bas password
#            return False
        try:
            mongo.projects.remove({"name": self.name,
                                   "username": self.username})
            return True
        except Exception as exp:
            # TODO handle 
            return False



    def get_builds(self):
        """ return all build ids """
        builds = mongo.builds.find({"username": self.username,
                                    "project_name": self.name}).sort("id_", DESCENDING)
        return [Build(x) for x in builds]


    def get_latest_build(self):
        build = mongo.builds.find_one({"username": self.username,
                                       "project_name": self.name},
                                       sort=[("id_", -1)])
        if build:
            return Build(build)
        return None


    def get_latest_build_id(self):
        build = self.get_latest_build()
        if build is not None:
            return build.id_
        return None


    @classmethod
    def search(cls, name=None, username=None, limit=30, offset=0, get_last_build=False, pattern=''):
        filter_ = {}
        if username is not None:
            filter_['username'] = username
        if name is not None:
            filter_['name'] = name
        if limit > 100:
            limit = 100
        if pattern:
            regx = re.compile(pattern, re.IGNORECASE)
            filter_= {"$or": []}
            filter_["$or"].append({"name": regx})
            filter_["$or"].append({"username": regx})
        db_projects = mongo.projects.find(filter_, limit=limit, skip=offset)
        projects = []
        if db_projects is not None:
            projects = [cls(db_project, sub_objects=False) for db_project in db_projects]
            if get_last_build:
                for p in projects:
                    p.builds = [p.get_latest_build()]
                projects.sort(key=lambda p: p.builds[0].created, reverse=True)
        return projects




'''



        project_path = Project.get_folder_path(self.user.username, self.name)
        builds_path = os.path.join(project_path, "builds")
        if not os.path.isdir(builds_path):
            return []

        return sorted([id_ for id_ in os.listdir(builds_path)], key=lambda x: int(x))


    def create_build(self, build_data):
            latest_build = self.get_latest_build()
            build_data.id_ = 1
            if latest_build is not None:
                build_data.id_ += 1
            build_data.user = self.user
            build_data.project = self
            build = Build(**build_data)
            build.create



    @staticmethod
    def get_folder_path(username, project_name):
        """ Return project folder path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name)

'''
