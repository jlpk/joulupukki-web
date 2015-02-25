import os
import shutil

import pecan
import wsme
import json
import wsme.types as wtypes

from joulupukki.controllers.v2.datamodel import types
#from joulupukki.controllers.v2.datamodel.build import Build
from joulupukki.controllers.v2.datamodel.user import User


class APIProject(types.Base):
    name = wsme.wsattr(wtypes.text, mandatory=False)

class Project(APIProject):
    # TODO create a 
    user = wsme.wsattr(User, mandatory=False)
    builds = wsme.wsattr([wtypes.text], mandatory=False)
    jobs = wsme.wsattr([wtypes.text], mandatory=False)

    @classmethod
    def sample(cls):
        return cls(
            name="myproject",
        )

    @staticmethod
    def get_folder_path(username, project_name):
        """ Return project folder path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name)

    @classmethod
    def create(cls, user, project_name, project_data):
        # Create user folder
        project_folder_abs = cls.get_folder_path(user.username, project_name)
        try:
            os.makedirs(project_folder_abs)
            if isinstance(project_data, dict):
                project_data['user'] = user
                return cls(**project_data)
            else:
                project_data.user = user
                return cls(**project_data.as_dict())
        except Exception as exp:
            shutil.rmtree(project_folder_abs)
            return False

    @classmethod
    def fetch(cls, user, project_name):
        project_folder_abs =  Project.get_folder_path(user.username, project_name)
        if not os.path.isdir(project_folder_abs):
            # User doesn't exists
            return None
        project = cls(name=project_name, user=user)
        project.builds = project.get_builds()
        return project

    def update(self, new_user_data):
        # Remove calculed args
        calculed_args = ['token',
                        ]
        for arg in calculed_args:
            delattr(new_user_data, arg)
        # Check password
        # TODO remove clear password ... OUPS
        # and put that logic in decorator
        if self.password != new_user_data.password:
            # TODO handle error
            return False
        # Set new values
        for key, val in new_user_data.as_dict().items():
            setattr(self, key, val)
        # Write user data
        try:
            self.save()
            return self
        except Exception as exp:
            # TODO handle 
            return False

    def save(self):
        """ Write user data on disk """
        data = json.dumps({"username": self.username,
                           "name": self.name or None,
                           "password": self.password or None,
                           "email": self.email or None,
                           "github": self.github or None,
                           "token": self.token or None,
                          })
        userdata_file =  User.get_data_file_path(self.username)
        with open(userdata_file, 'w') as f:
            try:
                f.write(data)
            except Exception as exp:
                # TODO handle error
                raise Exception("Error saving user data")
        return True

    def delete(self):
        """ delete project """
        user_folder_abs = User.get_folder_path(self.username)
        shutil.rmtree(user_folder_abs)
        return True

    def get_builds(self):
        """ return all build ids """
        project_path = Project.get_folder_path(self.user.username, self.name)
        builds_path = os.path.join(project_path, "builds")
        if not os.path.isdir(builds_path):
            return []

        return sorted([id_ for id_ in os.listdir(builds_path)], key=lambda x: int(x))

    def get_latest_build(self):
        build_ids = self.get_builds()
        if build_ids == []:
            return None
        return build_ids[-1]

    def create_build(self, build_data):
            latest_build = self.get_latest_build()
            build_data.id_ = 1
            if latest_build is not None:
                build_data.id_ += 1
            build_data.user = self.user
            build_data.project = self
            build = Build(**build_data)
            build.create
