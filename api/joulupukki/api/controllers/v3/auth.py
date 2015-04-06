import httplib
from urlparse import urlparse, parse_qs
import urllib

import pecan
import wsmeext.pecan as wsme_pecan
from pecan import rest


class LoginController(rest.RestController):

    @wsme_pecan.wsexpose(unicode, unicode)
    def post(self, code):
        if code is None:
            return None
        url = 'github.com'
        conn = httplib.HTTPSConnection(url)
        params = urllib.urlencode({"code": code,
                                   "client_id": "a8f938da48bd7aa3a376",
                                   "client_secret": "dcf37827fb787fd6ba42e8fe221ef015aa35ec73",
                                  })
        conn.request("POST", "/login/oauth/access_token", params)
        response = conn.getresponse()
        data = response.read()
        params = parse_qs(data)
        access_token = params.get("access_token")
        if access_token:
            print "SSSSSSSSSSSSSS", access_token
            return access_token
        return None



class AuthController(rest.RestController):

    login = LoginController()


