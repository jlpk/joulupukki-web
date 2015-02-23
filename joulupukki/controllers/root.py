from pecan import expose, redirect

from webob.exc import status_map



from joulupukki.controllers.v1 import v1
from joulupukki.controllers.v2 import v2


class RootController(object):
    v1 = v1.V1Controller()
    v2 = v2.V2Controller()
