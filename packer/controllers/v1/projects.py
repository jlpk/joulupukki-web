from pecan import expose, redirect
import wsmeext.pecan as wsme_pecan
import pecan
from pecan import rest

from packer.controllers.v1.datamodel import project

#from webob.exc import status_map


class ProjectBuildController(rest.RestController):

    @pecan.expose()
    def get(self):
        """Returns a specific host."""
        return pecan.request.context['project_name'] + " build launched"


class ProjectSubController(rest.RestController):
    build = ProjectBuildController()


class ProjectController(rest.RestController):

    def __init__(self, project_name):
        pecan.request.context['project_name'] = project_name
        self._id = project_name

    @wsme_pecan.wsexpose(project.Project)
    def get(self):
        """Returns a specific host."""
        proj = {"name": self._id,
                "git_url": "git://localhost/shinken"}
        return project.Project(**proj)

    @pecan.expose()
    def _lookup(self, *remainder):
        return ProjectSubController(), remainder

class ProjectsController(rest.RestController):

    @pecan.expose()
    def _lookup(self, project_name, *remainder):
        return ProjectController(project_name), remainder

    @wsme_pecan.wsexpose([project.Project])
    def get_all(self):
        """Returns all projects."""
        projects = [{"name": "shinken"}]

        return [project.Project(**j) for j in projects]
