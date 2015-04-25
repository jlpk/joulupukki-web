import httplib
from urlparse import urlparse, parse_qs
import urllib
import json


import pecan


def get_access_token(code):

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

    if len(access_token) > 0:
        return access_token[0]
    return None


def get_user(access_token):
    
    url = "api.github.com"
    conn = httplib.HTTPSConnection(url)
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    params = urllib.urlencode({
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              })

    conn.request("GET", "/user", params, headers)
    response = conn.getresponse()
    return response.read()


def get_user_repos(username, access_token):
    
    url = "api.github.com"
    conn = httplib.HTTPSConnection(url)
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    params = urllib.urlencode({
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              })
    url = "/".join(("user", username, "repos"))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    return response.read()


def get_user_orgs(username, access_token):
    
    url = "api.github.com"
    conn = httplib.HTTPSConnection(url)
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    params = urllib.urlencode({
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              })
    url = "/".join(("user", username, "orgs"))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    return response.read()


def update_user_info_from_github(username, access_token):
    pass
