import pecan
from joulupukki.api.controllers.v3.users import UsersController
from joulupukki.api.controllers.v3.projects import ProjectsController


class V3Controller(object):
    """Version 3 API controller root."""
    users = UsersController()
    projects = ProjectsController()

