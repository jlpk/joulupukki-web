from pecan import expose, redirect

from joulupukki.api.controllers.v3 import v3
# from joulupukki.worker.controllers.stats import StatsController


class RootController(object):
    v3 = v3.V3Controller()
    # stats = StatsController()
