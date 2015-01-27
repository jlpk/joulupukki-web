from pecan import expose, redirect

from webob.exc import status_map



from packer.controllers.v1 import v1


class RootController(object):
    v1 = v1.V1Controller()
