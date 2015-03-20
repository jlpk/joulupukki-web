import os
import json
import shutil

import pecan

from joulupukki.lib.logger import get_logger, get_logger_docker
from joulupukki.controllers.v2.datamodel.project import Project


def get_project_folder_path(project):
    """ Return project folder path"""
    if isinstance(project, User):
        return os.path.join(pecan.conf.workspace_path, projectname)
    elif isinstance(project, str) or isinstance(project, unicode):
        return os.path.join(pecan.conf.workspace_path, project)
    else:
        # Bad project/projectname submitted
        return None

def get_project_data_file_path(projectname):
    """ Return project data from project_data file path"""
    project_folder_abs = get_project_folder_path(projectname)
    return os.path.join(project_folder_abs, "projectdata.cfg")


def get_project_data(projectname):
    """ Return project data from project_data file"""
    projectdata_file = get_project_data_file_path(projectname)
    if not os.path.isfile(projectdata_file):
        # config not found ...
        # this is release strange
        # this environnement is in bad state
        # we should think about delete it
        return False

    # Read projectdata.cfg
    with open(projectdata_file, 'r') as f:
        try:
            project = json.load(f)
        except Exception as exp:
            # TODO handle error
            return False
    return project


def save_project_data(project_data):
    """ Write project data on disk """
    data = json.dumps({"projectname": project_data.projectname,
                       "name": project_data.name or None,
                       "password": project_data.password or None,
                       "email": project_data.email or None,
                       "github": project_data.github or None,
                       "token": project_data.token or None,
                      })
    projectdata_file = get_project_data_file_path(project_data.projectname)
    with open(projectdata_file, 'w') as f:
        try:
            f.write(data)
        except Exception as exp:
            # TODO handle error
            raise Exception("Error saving project data")

    return True




def get_project(projectname):
    project_folder_abs = get_project_folder_path(projectname)
    if not os.path.isdir(project_folder_abs):
        # User not found
        return None
    else:
        # TODO read config file in project folder
        try:
            return User(**get_project_data(projectname))
        except Exception as exp:
            # TODO handle error
            return False


def create_project(projectname, project_data):
    project_data.projectname = projectname
    # Check required args
    required_args = ['projectname',
                     'email',
                     'password',
                    ]
    for arg in required_args:
        if not getattr(project_data, arg):
            # TODO handle error
            return False
    # Remove calculed args
    calculed_args = ['token',
                    ]
    for arg in calculed_args:
        delattr(project_data, arg)

    # TODO encrypt password ...
    # Create project folder
    project_folder_abs = get_project_folder_path(projectname)
    os.makedirs(project_folder_abs)

    # Write project data
    try:
        save_project_data(project_data)
        return User(**project_data.__dict__)
    except Exception as exp:
        shutil.rmtree(project_folder_abs)
        # TODO handle error
        return False


def delete_project(project_data):
    pass
