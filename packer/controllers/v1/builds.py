from pecan import expose, redirect
import wsmeext.pecan as wsme_pecan
import pecan
from pecan import rest


import uuid

from packer.controllers.v1.datamodel.build import Build


from packer.worker.manager import build_tasks

#from webob.exc import status_map


class BuildBuildController(rest.RestController):

    @pecan.expose()
    def get(self):
        """Returns a specific host."""
        return pecan.request.context['build_name'] + " build launched"


class BuildSubController(rest.RestController):
    build = BuildBuildController()


class BuildController(rest.RestController):

    def __init__(self, build_id):
        pecan.request.context['build_name'] = build_id
        self._id = build_id

    @wsme_pecan.wsexpose(Build)
    def get(self):
        """Returns build status"""
#        proj = {"name": self._id,
#                "git_url": "git://localhost/shinken"}
#        return Build(**proj)

    @pecan.expose()
    def _lookup(self, *remainder):
        return BuildSubController(), remainder

import wsme.types as wtypes
class BuildsController(rest.RestController):

    @pecan.expose()
    def _lookup(self, build_name, *remainder):
        return BuildController(build_name), remainder

    #curl -X POST -H "Content-Type: application/json" -i  -d '{"git_url": "https://github.com/kaji-project/kaji.git", "branch": "packer"}' http://127.0.0.1:8080/v1/builds/
    @wsme_pecan.wsexpose(wtypes.text, body=Build, status_code=201)
    def post(self, build):
        """ launch build """
        build.uuid = str(uuid.uuid4())
        build_tasks.put(build)
        # TODO: save build in database ???
        return str(build.uuid)

    @wsme_pecan.wsexpose([Build])
    def get_all(self):
        """Returns all builds."""
        builds = [{"name": "shinken"}]
        #return [build.Build(**j) for j in projects]
