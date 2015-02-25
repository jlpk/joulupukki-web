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
from joulupukki.controllers.v2.datamodel.build import Build, APIBuild
from joulupukki.controllers.v2.datamodel.user import User
from joulupukki.controllers.v2.datamodel.project import Project
from joulupukki.controllers.v2.datamodel.job import Job
from joulupukki.controllers.v2.jobs import JobsController
from joulupukki.controllers.v2.download import DownloadController


from joulupukki.lib.queues import build_tasks
from joulupukki.lib.distros import supported_distros, reverse_supported_distros



class BuildController(rest.RestController):
    def __init__(self, build_id=None):
        pecan.request.context['build_id'] = build_id
        self.id_ = build_id

    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/
    @wsme_pecan.wsexpose(Build)
    def get(self):
        """Returns build status"""
        project_name = pecan.request.context['project_name']
        user = User.fetch(pecan.request.context['username'])
        project = Project.fetch(user, project_name)
        build_id = self.id_
        if self.id_ in ["latest"]:
            build_id = project.get_latest_build()
        build = Build.fetch(project, build_id, sub_objects=True)
        if build:
           return build
        return None

    # curl -X DELETE http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/
    @pecan.expose()
    def delete(self):
        """Delete build and build folder"""
        build = get_build(self._id)
        if os.path.exists(os.path.join(pecan.conf.builds_path, self._id)):
            shutil.rmtree(os.path.join(pecan.conf.builds_path, self._id))
            return "Deleted"
        return "Doesn't exist"


    @pecan.expose()
    def _lookup(self, *remainder):
         return BuildSubController(), remainder





class BuildsController(rest.RestController):
#    def __init__(self, ):
    #curl -X POST -H "Content-Type: application/json" -i  -d '{"source_url": "https://github.com/kaji-project/kaji.git", "source_type": "git", "branch": "packer"}' http://127.0.0.1:8080/v1/builds/
    #curl -X POST -H "Content-Type: application/json" -i  -d '{"source_url": "/home/tcohen/projet_communautaire/kaji/meta/packages/grafana", "source_type": "local", "branch": "packer"}' http://127.0.0.1:8080/v2/titilambert/myproject/builds/

    @wsme_pecan.wsexpose([Build])
    def get_all(self):
        """Returns all builds."""
        project_name = pecan.request.context['project_name']
        user = User.fetch(pecan.request.context['username'])
        project = Project.fetch(user, project_name)
        builds = [Build.fetch(project, b_id, False) for b_id in project.get_builds()]
        builds = [b for b in builds if b]
        return builds

    @pecan.expose()
    def _lookup(self, build_id, *remainder):
        return BuildController(build_id), remainder


class LaunchBuildController(rest.RestController):

    @wsme_pecan.wsexpose(wtypes.text, body=APIBuild, status_code=201)
    def post(self, build):
        """ launch build """
        project_name = pecan.request.context['project_name']
        user = User.fetch(pecan.request.context['username'])
        project = Project.fetch(user, project_name)

        if project is None:
            # The project doesn't exist
            # We have to create it
            # TODO Maybe it's better to force users to create project before
            # they can create builds
            project = Project.create(user, project_name, {"name": project_name})

        build = Build.create(project, build)
        build_tasks.put(build)
        # TODO: save build in database ???
        # for now is in build.cfg ...
        return "Build created"



class BuildSubController(rest.RestController):
    download = DownloadController()
    jobs = JobsController()

