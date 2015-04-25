import httplib
from urlparse import urlparse, parse_qs
import urllib
import json

import pecan

from joulupukki.common.datamodel.user import User
from joulupukki.common.datamodel.project import Project



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


def get_user_from_token(access_token):
    
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
    return json.loads(response.read())


def get_user(username, access_token):
    
    url = "api.github.com"
    conn = httplib.HTTPSConnection(url)
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    params = urllib.urlencode({
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              })

    url = "/".join(("/users", username))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    return json.loads(response.read())

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
    url = "/".join(("/users", username, "repos"))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    return json.loads(response.read())


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
    url = "/".join(("/users", username, "orgs"))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    return json.loads(response.read())


def update_user_info_from_github(username, access_token):
    user = User.fetch_from_github_token(access_token)
    if user is None or user.username != username:
        return False
    # Get data from github
    gh_user = get_user(username, access_token)
    gh_repos = get_user_repos(username, access_token)
    gh_orgs = get_user_orgs(username, access_token)

    # Update user data
    user.email = gh_user['email']
    user.github_url = gh_user['html_url']
    user.name = gh_user['name']
    user.orgs = [org['login'] for org in gh_orgs]
    # Update repos and create it if not exists
    for repo in gh_repos:
        project = Project.fetch(user.username, repo['name'])
        if project is None:
            project = Project({"name": repo['name'],
                               "description": repo['description'],
                               "username": user.username,
                               "enabled": False,
                               "url": repo['html_url'],
                               })
            project.create()
        # TODO get Project status (enable) from github
        # Save project
        project.update()
    user._save()
    return True


def toggle_project_webjook(user, project, access_token):
    # TODO put in confg
    webhook_url = "http://jlpk.org"
    
    url = "api.github.com"
    # Get webhook
    conn = httplib.HTTPSConnection(url)
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    params = urllib.urlencode({
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              })
    url = "/".join(("/repos", user.username, project.name, "hooks"))
    conn.request("GET", url, params, headers)
    response = conn.getresponse()
    hooks = json.load(response)

    new_state = True
    hook_id = None
    if response.status >= 400:
        return None
    for hook in hooks:
        if hook.get('name') == 'web' and hook.get('config').get('url') == webhook_url:
            new_state = not hook.get('active')
            hook_id = str(hook.get('id'))
    # Set url depending of create/update
    if hook_id is None:
        url = "/".join(("/repos", user.username, project.name, "hooks"))
    else:
        url = "/".join(("/repos", user.username, project.name, "hooks", hook_id))
    # Create/Update webhook
    headers = {}
    headers['Authorization'] = "token " + access_token
    headers['User-Agent'] = "Joulupukki"
    config = {"url": webhook_url,
              "content_type": "json",
              "secret": user.token,
              "insecure_ssl": '0',
             }
    params = {
                               "name": "web",
                               "config": config,
                               "events": "push",
                               "active": new_state,
                               "client_id": pecan.conf.github_id,
                               "client_secret": pecan.conf.github_secret,
                              }
    conn.request("POST", url, json.dumps(params), headers)
    response = conn.getresponse()
    data = json.load(response)

    if response.status >= 400:
        return None
    # Save project on mongodb
    project.enabled = new_state
    project.update()

    return new_state

