import pecan
from pecan import rest


class HelloController(rest.RestController):

    @pecan.expose()
    def get(self):
        """Says hello."""
        print "Hello World!"

        return "Hello World!"
