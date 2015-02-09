from pecan import expose, redirect
import wsmeext.pecan as wsme_pecan
import pecan
from pecan import rest

import wsme.types as wtypes

from wsme.types import File


import zipfile
import tarfile

import glob
import os
import json
import uuid
import datetime

from io import BytesIO
from joulupukki.controllers.v1.datamodel.build import Build


from joulupukki.lib.queues import build_tasks
from joulupukki.lib.distros import supported_distros, reverse_supported_distros






archive_types = {"zip": "application/zip",
                 "tgz": "application/x-gzip",
                }


class LogDistroBuildController(rest.RestController):
    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/distros/centos_6/log/?html=1
    @expose(content_type='text/plain')
    def get(self):
        """Returns log of a specific distro."""
        return get_distro_log(pecan.request.context['build_uuid'], pecan.request.context['distro_name'])


class DownloadDistroBuildController(rest.RestController):

    # http://127.0.0.1:8080/v1/builds/6f26f2c8-34dd-4b54-9d74-56dd9969cb5e/distros/debian_7/download/?archive=zip
    @expose()
    def get(self, archive="tgz"):
        """Returns log of a specific distro."""
        # Prepare content type
        content_type = archive_types.get(archive, "tgz")
        pecan.core.override_template(None, content_type)
        # Get output folder
        output_folder = os.path.join(pecan.conf.builds_path,
                                     pecan.request.context['build_uuid'],
                                     supported_distros[pecan.request.context['distro_name']],
                                     'output')
        # Test if output folder exists
        if not os.path.isdir(output_folder):
            return
        # Prepare archive
        f = BytesIO()
        if archive == 'zip':
            # Zip
            zip_archive = zipfile.ZipFile(f, "w" )
            for file_ in glob.glob(output_folder + "/*"):
                zip_archive.write(file_, os.path.basename(file_))
            zip_archive.close()
            extension = "zip"
        else:
            # Tarball
            tar_archive = tarfile.open(fileobj=f, mode="w:gz")
            for file_ in glob.glob(output_folder + "/*"):
                tar_archive.add(file_, os.path.basename(file_))
            tar_archive.close()
            extension = "tar.gz"

        # Set headers
        build = get_build(pecan.request.context['build_uuid'])
        distro = pecan.request.context['distro_name']
        headers = pecan.response.headers
        if build.get('package_name') is None:
            return
        filename = "%(package_name)s_%(package_version)s-%(package_release)s" % build
        filename = filename + "-" + distro
        filename = ".".join((filename, extension))
        headers.add("Content-Disposition", str("attachment;filename=%s" % filename))
        # returns
        return f.getvalue()




class DistroBuildSubController(rest.RestController):
    log = LogDistroBuildController()
    download = DownloadDistroBuildController()

class DistroBuildController(rest.RestController):

    def __init__(self, distro_name):
        pecan.request.context['distro_name'] = distro_name
        self.distro_name = distro_name

    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/distros/debian_7
    @pecan.expose()
    def get(self):
        """Returns a specific distro."""
        return get_distro_status(pecan.request.context['build_uuid'], self.distro_name)


    @pecan.expose()
    def _lookup(self, *remainder):
        return DistroBuildSubController(), remainder


class DistrosBuildController(rest.RestController):

    @pecan.expose()
    def _lookup(self, distro_name, *remainder):
        return DistroBuildController(distro_name), remainder

    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/distros
    @wsme_pecan.wsexpose([str])
    def get_all(self):
        """List distros of a build"""
        return get_distros(pecan.request.context['build_uuid'])


class LogBuildController(rest.RestController):
    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/log/?html=1
    #@pecan.expose()
    @expose(content_type='text/plain')
    def get(self):
        """Returns log of a build."""
        return get_distro_log(pecan.request.context['build_uuid'])


class BuildSubController(rest.RestController):
    distros = DistrosBuildController()
    log = LogBuildController()

class BuildController(rest.RestController):
    def __init__(self, build_id):
        pecan.request.context['build_uuid'] = build_id
        self._id = build_id

    # curl -X GET http://127.0.0.1:8080/v1/builds/c1afd1d8-17ee-4858-8dd1-964cb065d141/
    @wsme_pecan.wsexpose(Build)
    def get(self):
        """Returns build status"""
        build = get_build(self._id)
        if build is not None:
            return Build(**build)
        else:
            return None

    @pecan.expose()
    def _lookup(self, *remainder):
        return BuildSubController(), remainder


class BuildsController(rest.RestController):

    @pecan.expose()
    def _lookup(self, build_uuid, *remainder):
        return BuildController(build_uuid), remainder

    #curl -X POST -H "Content-Type: application/json" -i  -d '{"source_url": "https://github.com/kaji-project/kaji.git", "source_type": "git", "branch": "packer"}' http://127.0.0.1:8080/v1/builds/
    #curl -X POST -H "Content-Type: application/json" -i  -d '{"source_url": "/home/tcohen/projet_communautaire/kaji/meta/packages/grafana", "source_type": "local", "branch": "packer"}' http://127.0.0.1:8080/v1/builds/
    @wsme_pecan.wsexpose(wtypes.text, body=Build, status_code=201)
    def post(self, build):
        """ launch build """
        build.uuid = str(uuid.uuid4())
        build_tasks.put(build)
        # TODO: save build in database ???
        # for now is in build.cfg ...
        return str(build.uuid)

    @wsme_pecan.wsexpose([Build])
    def get_all(self):
        """Returns all builds."""
        builds = []
        for uuid in os.listdir(pecan.conf.builds_path):
            build = get_build(uuid)
            if build is not None:
                builds.append(build)

        return [Build(**b) for b in builds]



def get_build(uuid):
    # Check folder exists
    build_folder_abs = os.path.join(pecan.conf.builds_path, uuid)
    if not os.path.isdir(build_folder_abs):
        return
    # Check if build.cfg exists
    build_config_file = os.path.join(build_folder_abs, "build.cfg")
    if not os.path.isfile(build_config_file):
        return
    # Read build.cfg
    with open(build_config_file, 'r') as f:
        try:
            build = json.load(f)
        except Exception as exp:
            return
    build['created'] = datetime.datetime.fromtimestamp(build['created']).isoformat()
    return build


def get_distros(uuid):
    # Check folder exists
    build_folder_abs = os.path.join(pecan.conf.builds_path, uuid)
    if not os.path.isdir(build_folder_abs):
        return
    # Get distro list
    distros = []
    for distro in os.listdir(build_folder_abs):
        if distro in reverse_supported_distros:
            distros.append(reverse_supported_distros[distro])

    return distros


def get_distro_status(uuid, distro_name):
    # Check folder exists
    build_folder_abs = os.path.join(pecan.conf.builds_path, uuid)
    if not os.path.isdir(build_folder_abs):
        return
    if distro_name not in supported_distros:
        return
    distro_folder_abs = os.path.join(build_folder_abs, supported_distros[distro_name])
    if not os.path.isdir(distro_folder_abs):
        return
    distro_status_file = os.path.join(distro_folder_abs, 'status.txt')
    if not os.path.isfile(distro_status_file):
        return
    # Read status_file
    with open(distro_status_file, 'r') as f:
        try:
            status = f.read()
        except Exception as exp:
            return
    return status




def get_distro_log(uuid, distro_name=None):
    # Check folder exists
    build_folder_abs = os.path.join(pecan.conf.builds_path, uuid)
    if not os.path.isdir(build_folder_abs):
        return
    # Check logs
    if distro_name is not None:
        # Distro logs
        if distro_name not in supported_distros:
            return
        distro_folder_abs = os.path.join(build_folder_abs, supported_distros[distro_name])
        if not os.path.isdir(distro_folder_abs):
            return
        log_file = os.path.join(distro_folder_abs, 'log.txt')
    else:
        # Build logs
        log_file = os.path.join(build_folder_abs, 'log.txt')
    if not os.path.isfile(log_file):
        return
    # Read status_file
    with open(log_file, 'r') as f:
        try:
            log = f.read()
        except Exception as exp:
            return
    return log
