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
from joulupukki.common.datamodel.user import User, APIUser


from joulupukki.api.controllers.v3.projects import ProjectController



class UsersController(rest.RestController):

    @pecan.expose()
    def _lookup(self, username, *remainder):
        return UserController(username), remainder


class UserController(rest.RestController):
    def __init__(self, username):
        pecan.request.context['username'] = username
        self.username = username

    # curl -X GET http://127.0.0.1:8080/v3/users/joulupukki
    @wsme_pecan.wsexpose(User)
    def get(self):
        """Returns user"""
        user = User.fetch(self.username, with_password=False)
        return user

    # curl -X POST -H "Content-Type: application/json" -i  -d '{"username": "titilambert", "email": "titilambert@localhost.local", "password": "titilambert", "name": "Thibault Cohen"}' http://127.0.0.1:8081/v3/users/titilambert
    @wsme_pecan.wsexpose(wtypes.text, body=APIUser, status_code=201)
    def post(self, sent_user):
        """Create/Edit user"""
        user = User.fetch(self.username)
        if user is None:
            sent_user.username = self.username
            new_user = User(sent_user.as_dict()) 
            if not new_user.create():
                # Handle error
                return {"result": "Error creating user %s with data %s" % (sent_user.username, sent_user)}
            return {"result": "User %s created" % sent_user.username}
        else:
            if not user.update(sent_user):
                # Handle error
                return {"result": "Error editing"}
            return {"result": "User %s edited" % self.username}

    # curl -X DELETE -H "Content-Type: application/json" -i  -d '{"username": "titilambert", "password": "titilambert"}' http://127.0.0.1:8081/v3/titilambert
    @wsme_pecan.wsexpose(wtypes.text, body=APIUser, status_code=201)
    def delete(self, sent_user):
        """Delete user and user folder"""
        user = User.fetch(self.username)
        if user is not None:
            if user.delete(sent_user.password):
                return {"result": "User %s deleted" % self.username}
        return {"result": "User Doesn't exist"}

    @pecan.expose()
    def _lookup(self, project_name, *remainder):
        return ProjectController(project_name), remainder

