import pecan
from joulupukki.controllers.v2.users import UserController


class V2Controller(object):
    """Version 2 API controller root."""

    @pecan.expose()
    def _lookup(self, username, *remainder):
        return UserController(username), remainder


