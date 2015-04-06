import pecan
from joulupukki.api.controllers.v3.users import UsersController
from joulupukki.api.controllers.v3.projects import ProjectsController
from joulupukki.api.controllers.v3.stats import StatsController
from joulupukki.api.controllers.v3.auth import AuthController


class V3Controller(object):
    """Version 3 API controller root."""
    users = UsersController()
    projects = ProjectsController()
    stats = StatsController()
    auth = AuthController()
