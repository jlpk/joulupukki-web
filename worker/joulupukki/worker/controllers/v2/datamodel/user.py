import os
import shutil

import pecan
import wsme
import json
import wsme.types as wtypes

from joulupukki.web.controllers.v2.datamodel import types
#from joulupukki.web.controllers.v2.datamodel.project import Project


class APIUser(types.Base):
    username = wsme.wsattr(wtypes.text, mandatory=False)
    github = wsme.wsattr(wtypes.text, mandatory=False)
    email = wsme.wsattr(wtypes.text, mandatory=False)
    name = wsme.wsattr(wtypes.text, mandatory=False)
    token = wsme.wsattr(wtypes.text, mandatory=False)
    password = wsme.wsattr(wtypes.text, mandatory=False)

class User(APIUser):
    projects = wsme.wsattr([wtypes.text], mandatory=False)

    @staticmethod
    def get_folder_path(username):
        """ Return user folder path"""
        return os.path.join(pecan.conf.workspace_path, username)

    def dumps(self):
        dump = self.as_dict()
        return dump

    @staticmethod
    def get_data_file_path(username):
        user_folder_abs = User.get_folder_path(username)
        return os.path.join(user_folder_abs, "userdata.cfg")    

    @classmethod
    def sample(cls):
        return cls(
            username="joulupukkit",
            email="admin@joulupukkit.local",
            password="packer",
        )

    @classmethod
    def fetch(cls, username):
        user_folder_abs =  User.get_folder_path(username)
        if not os.path.isdir(user_folder_abs):
            # User doesn't exists
            return None
        userdata_file = User.get_data_file_path(username)
        if not os.path.isfile(userdata_file):
            # config not found ...
            # this is release strange
            # this environnement is in bad state
            # we should think about delete it
            return False
        # Read userdata.cfg
        with open(userdata_file, 'r') as f:
            try:
                user_data = json.load(f)
                user = cls(**user_data)
                user.projects = user.get_projects()
                return user
            except Exception as exp:
                # TODO handle error
                return False

    @classmethod
    def create(cls, username, user_data):
        user_data.username = username
        # Check required args
        required_args = ['username',
                         'email',
                         'password',
                        ]
        for arg in required_args:
            if not getattr(user_data, arg):
                # TODO handle error
                return False
        # Remove calculed args
        calculed_args = ['token',
                        ]
        for arg in calculed_args:
            delattr(user_data, arg)
        # TODO encrypt password ...
        # Create user folder
        user_folder_abs = cls.get_folder_path(username)
        os.makedirs(user_folder_abs)
        # Write user data
        try:
            new_user = cls(**user_data.as_dict())
            new_user.save()
            return new_user
        except Exception as exp:
            shutil.rmtree(user_folder_abs)
            # TODO handle error
            return False

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

    def get_projects(self):
        for root, folders, files in os.walk(User.get_folder_path(self.username)):
            return folders
