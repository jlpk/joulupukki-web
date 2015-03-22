from pecan import expose, redirect

from joulupukki.worker.controllers.stats import StatsController

rom joulupukki.api.controllers.v2 import v2


class RootController(object):
    v2 = v2.V2Controller()
    stats = StatsController()
