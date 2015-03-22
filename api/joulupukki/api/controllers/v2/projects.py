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


from joulupukki.common.datamodel.user import User
from joulupukki.common.datamodel.result import APIResult
from joulupukki.common.datamodel.project import Project, APIProject


from joulupukki.api.controllers.v2.builds import BuildsController
from joulupukki.api.controllers.v2.builds import LaunchBuildController

from joulupukki.common.distros import supported_distros, reverse_supported_distros



class ProjectController(rest.RestController):
    def __init__(self, project_name):
        pecan.request.context['project_name'] = project_name
        self.project_name = project_name
        self.user = User.fetch(pecan.request.context['username'], sub_objects=False)
        if self.user is None:
            raise Exception("User not found")
        

    # curl -X GET http://127.0.0.1:8080/v2/joulupukki/myproject
    @wsme_pecan.wsexpose(Project)
    def get(self):
        """Returns project"""
        project = Project.fetch(self.user, self.project_name)
        return project

    # curl -X POST -H "Content-Type: application/json" -i  -d '{"name": "project"}' http://127.0.0.1:8081/v2/titilambert/myproject
    @wsme_pecan.wsexpose(wtypes.text, body=APIProject, status_code=201)
    def post(self, sent_project):
        """Create project"""
        projects = self.user.get_projects()
        if self.project_name not in [p.name for p in projects]:
            sent_project.name = self.project_name
            new_project = Project(sent_project.as_dict())
            new_project.username = self.user.username
            if not new_project.create():
                # Handle error
                return {"result": "Error creating %s with data %s" % (self.project_name, sent_project)}
            return {"result": "Project %s created" % self.project_name}
        else:
            return {"result": "Project %s exists" % self.project_name}

    # curl -X DELETE http://127.0.0.1:8081/v2/titilambert/myproject
    @wsme_pecan.wsexpose(APIResult)
    def delete(self):
        """Delete project""" 
        project = Project.fetch(self.user, self.project_name)
        if project is not None:
            if project.delete():
                return APIResult(result="Project %s deleted" % self.project_name)
        return APIResult(result="Project doesn't exist")

    @pecan.expose()
    def _lookup(self, *remainder):
        return ProjectSubController(), remainder





class ProjectSubController(rest.RestController):
    builds = BuildsController()
    build = LaunchBuildController()
#    jobs = JobsController()






