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
from joulupukki.controllers.v2.datamodel.project import Project


from joulupukki.controllers.v2.builds import BuildsSubController

from joulupukki.lib.distros import supported_distros, reverse_supported_distros



class ProjectController(rest.RestController):
    def __init__(self, project_name):
        pecan.request.context['project_name'] = project_name
        self.project_name = project_name
        self.user = User.fetch(pecan.request.context['username'])
        if self.user is None:
            raise Exception("User not found")
        

    # curl -X GET http://127.0.0.1:8080/v2/joulupukki/myproject
    @wsme_pecan.wsexpose(Project)
    def get(self):
        """Returns project"""
        project = self.user.get_project(self.project_name)
        return project


    # curl -X POST -H "Content-Type: application/json" -i  -d '{}' http://127.0.0.1:8080/v2/titilambert/myproject
    @wsme_pecan.wsexpose(wtypes.text, body=Project, status_code=201)
    def post(self, project_data):
        """Create project"""
        projects = self.user.get_projects()
        if not projects or self.project_name not in projects:
            if not self.user.create_project(self.project_name, project_data):
                # Handle error
                return "Error creating"
            return "Project %s created" % self.project_name
        else:
            return "Project %s exists" % self.project_name

    # curl -X DELETE http://127.0.0.1:8080/v1/joulupukki/myproject
    @pecan.expose()
    def delete(self):
        """Delete project and project folder"""
        project = get_project(self.project_name)
        if project is not None:
            delete_project(project)
            return "Project %s deleted" % self.project_name
        return "Project doesn't exist"

    @pecan.expose()
    def _lookup(self, *remainder):
        return BuildsSubController(), remainder





