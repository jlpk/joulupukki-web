from pecan import expose, redirect
import wsmeext.pecan as wsme_pecan
import pecan
from pecan import rest

import wsme.types as wtypes

from wsme.types import File


import zipfile
import tarfile

import glob
import os
import json
import uuid
import datetime
import shutil

from io import BytesIO
from joulupukki.controllers.v2.datamodel.user import User


from joulupukki.controllers.v2.projects import ProjectController


from joulupukki.lib.queues import build_tasks
from joulupukki.lib.distros import supported_distros, reverse_supported_distros



class UserController(rest.RestController):
    def __init__(self, username):
        pecan.request.context['username'] = username
        self.username = username

    # curl -X GET http://127.0.0.1:8080/v2/joulupukki
    @wsme_pecan.wsexpose(User)
    def get(self):
        """Returns user"""
        user = User.fetch(self.username)
        # TODO hide password/token if password is not correct...
        # delattr(user, 'password')
        return user

    # curl -X POST -H "Content-Type: application/json" -i  -d '{"username": "titilambert", "email": "titilambert@localhost.local", "password": "titilambert"}' http://127.0.0.1:8080/v2/titilambert
    @wsme_pecan.wsexpose(wtypes.text, body=User, status_code=201)
    def post(self, user_data):
        """Create/Edit user"""
        user = User.fetch(self.username)
        if user is None:
            if not User.create(self.username, user_data):
                # Handle error
                return "Error creating"
            return "User %s created" % self.username
        else:
            if not user.update(user_data):
                # Handle error
                return "Error editing"
            return "User %s edited" % self.username

    # curl -X DELETE http://127.0.0.1:8080/v1/joulupukki
    @pecan.expose()
    def delete(self):
        """Delete user and user folder"""
        user = User.fetch(self.username)
        if user is not None:
            user.delete()
            return "User %s deleted" % self.username
        return "User Doesn't exist"

    @pecan.expose()
    def _lookup(self, project_name, *remainder):
        return ProjectController(project_name), remainder

