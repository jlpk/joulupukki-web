import os
import shutil

import pecan
import wsme
import json
import wsme.types as wtypes

from joulupukki.common.database import mongo
from joulupukki.common.utils import encrypt_password, check_password, create_token
from joulupukki.common.datamodel import types
#from joulupukki.web.controllers.v2.datamodel.project import Project
from joulupukki.common.datamodel.project import Project


class APIUser(types.Base):
    username = wsme.wsattr(wtypes.text, mandatory=True)
    password = wsme.wsattr(wtypes.text, mandatory=True)
    github = wsme.wsattr(wtypes.text, mandatory=False)
    email = wsme.wsattr(wtypes.text, mandatory=False)
    name = wsme.wsattr(wtypes.text, mandatory=False)

class User(APIUser):
    projects = wsme.wsattr([Project], mandatory=False)
    token = wsme.wsattr(wtypes.text, mandatory=False)

    def __init__(self, data=None):
        if data is None:
            APIUser.__init__(self)
        if isinstance(data, APIUser):
            APIUser.__init__(self, **data.as_dict())
        else:
            APIUser.__init__(self, **data)
        self.projects = self.get_projects()

    @classmethod
    def sample(cls):
        return cls(
            username="joulupukkit",
            email="admin@joulupukkit.local",
            password="packer",
        )

    @classmethod
    def fetch(cls, username, with_password=True):
        db_user = mongo.users.find_one({"username": username})
        user = None
        if db_user is not None:
            user = cls(db_user)
            if not with_password:
                delattr(user, 'password')
        return user

    def create(self):
        # Check required args
        required_args = ['username',
                         'email',
                         'password',
                        ]
        for arg in required_args:
            if not getattr(self, arg):
                # TODO handle error
                return False
        # Create token
        self.token = create_token(mongo) 
        # Encrypt password
        self.password = encrypt_password(self.password)
        # Write user data
        try:
            self._save()
            return True
        except Exception as exp:
            # TODO handle error
            return False

    def update(self, new_user_data):
        # Remove no editable args
        calculed_args = ['token',
                         'username',
                         'Id',
                        ]
        for arg in calculed_args:
            if hasattr(new_user_data, arg):
                delattr(new_user_data, arg)
        # Check password
        if not check_password(new_user_data.password, self.password):
            # TODO bas password
            return False
        # Set new values
        for key, val in new_user_data.as_dict().items():
            # We don't want to modify password
            if key == 'password':
                continue
            setattr(self, key, val)
        # Write user data
        try:
            self._save()
            return self
        except Exception as exp:
            # TODO handle 
            return False

    def _save(self):
        """ Write user data on disk """
        mongo.users.update({"username": self.username}, self.as_dict(), upsert=True)
        return True


    def delete(self, password):
        # Check password
        if not check_password(password, self.password):
            # TODO bas password
            return False
        try:
            mongo.users.remove({"username": self.username})
            return True
        except Exception as exp:
            # TODO handle 
            return False

    def get_projects(self):
        projects = mongo.projects.find({"username": self.username})
        return [Project(x) for x in projects]

