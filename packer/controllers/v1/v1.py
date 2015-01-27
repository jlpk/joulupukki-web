from packer.controllers.v1 import projects
from packer.controllers.v1 import hello


class V1Controller(object):
    """Version 1 API controller root."""
    hello = hello.HelloController()
    projects = projects.ProjectsController()
