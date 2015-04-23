from pecan import expose, redirect

from webob.exc import status_map

from joulupukki.worker.controllers.stats import StatsController


from joulupukki.worker.controllers.v2 import v2


class RootController(object):
    v2 = v2.V2Controller()
    stats = StatsController()
