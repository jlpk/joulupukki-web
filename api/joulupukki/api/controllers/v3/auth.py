import httplib
from urlparse import urlparse, parse_qs
import urllib
import json

import pecan
import wsmeext.pecan as wsme_pecan
from pecan import rest

from joulupukki.common.datamodel.user import User

class LoginController(rest.RestController):

    @wsme_pecan.wsexpose(unicode, unicode)
    def post(self, code):
        if code is None:
            return None
        headers = {"User-Agent": "Joulupukki"}
        url = 'github.com'
        conn = httplib.HTTPSConnection(url)
        params = urllib.urlencode({"code": code,
                                   "client_id": pecan.conf.github_id,
                                   "client_secret": pecan.conf.github_secret,
                                  })
        conn.request("POST", "/login/oauth/access_token", params, headers)
        response = conn.getresponse()
        data = response.read()
        params = parse_qs(data)
        access_token = params.get("access_token")
        if access_token:
            # Check if this user exists in DB
            # if not we need to create it
            user = User.fetch_from_github_token(access_token[0])
            print user
            if user is None:
                # Get data from github
                url = "api.github.com"
                conn = httplib.HTTPSConnection(url)
                headers['Authorization'] = "token " + access_token[0]
                params = urllib.urlencode({
                                           "client_id": pecan.conf.github_id,
                                           "client_secret": pecan.conf.github_secret,
                                          })


                conn.request("GET", "/user", params, headers)
                response = conn.getresponse()
                raw_data = response.read()
                if raw_data:
                    # Save this new user
                    data = json.loads(raw_data)
                    new_user = User({"username": data['login'],
                                     "name": data['name'],
                                     "github_url": data['html_url'],
                                     "email": data['email'],
                                     "token_github": access_token[0]
                                    })
                    if not new_user.create():
                        return None
                else:
                    return None
            # TODO access_token is a list should be a str
            return access_token
        return None



class AuthController(rest.RestController):

    login = LoginController()


