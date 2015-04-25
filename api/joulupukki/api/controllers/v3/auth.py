import httplib
from urlparse import urlparse, parse_qs
import urllib
import json

import pecan
import wsmeext.pecan as wsme_pecan
from pecan import rest

from joulupukki.common.datamodel.user import User
from joulupukki.api.libs import github

class LoginController(rest.RestController):

    @wsme_pecan.wsexpose(unicode, unicode)
    def post(self, code):
        if code is None:
            return None

        access_token = github.get_access_token(code)

        if access_token:
            # Check if this user exists in DB
            # if not we need to create it
            user = User.fetch_from_github_token(access_token)
            if user is None:
                # Get data from github
                raw_data = github.get_user(access_token)
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


