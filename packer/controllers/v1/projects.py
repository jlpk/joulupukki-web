from pecan import expose, redirect
import wsmeext.pecan as wsme_pecan
import pecan
from pecan import rest

from packer.controllers.v1.datamodel import project

#from webob.exc import status_map



#class ProjectController(rest.RestController):
#
#    @wsme_pecan.wsexpose()
#    def get(self):
#        """Returns a specific host."""
#        print "SSSS"
#        return "shinken"


class ProjectsController(rest.RestController):



    #@pecan.expose()
    #def _lookup(self, *remainder):
    #    print "SSSS1", remainder
    #    return ProjectController(), remainder


    #@pecan.expose()
    #def get(self):
    #    """Says hello."""
    #    print "SSSS3"
    #    return "Hello World!"

    #@pecan.expose()
    @wsme_pecan.wsexpose([project.Project])
    def get_all(self):
        """Returns all projects."""
        projects = [{"name": "shinken"}]

        return [project.Project(**j) for j in projects]
