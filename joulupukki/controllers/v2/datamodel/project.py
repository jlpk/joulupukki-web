import os
import shutil

import pecan
import wsme
import json
import wsme.types as wtypes

from joulupukki.controllers.v2.datamodel import types


class Project(types.Base):
    name = wsme.wsattr(wtypes.text, mandatory=False)
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
        return cls(name=project_name)

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
        user_folder_abs = User.get_folder_path(self.username)
        shutil.rmtree(user_folder_abs)
        return True
