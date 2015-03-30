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
import shutil

from io import BytesIO, RawIOBase
from joulupukki.common.datamodel.build import Build, APIBuild
import StringIO 
from joulupukki.common.datamodel.user import User
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.job import Job
from joulupukki.api.controllers.v3.jobs import JobsController


from joulupukki.common.distros import supported_distros, reverse_supported_distros


archive_types = {"zip": "application/zip",
                 "tgz": "application/x-gzip",
                }


class OutputController(rest.RestController):
    # CURL -x GET http://127.0.0.1:8080/v3/titilambert/kaji/builds/6/output
    @wsme_pecan.wsexpose({str: [str]})
    def get(self):
        """Returns output content"""
        user = User.fetch(pecan.request.context['username'], sub_objects=False)
        if user is None:
            return None
        project_name = pecan.request.context['project_name']
        project = Project.fetch(user, project_name, sub_objects=False)
        if project is None:
            return None
        build_id = pecan.request.context['build_id']
        if build_id in ["latest"]:
            build_id = project.get_latest_build_id()
        build = Build.fetch(project, build_id, sub_objects=False)
        if build is None:
            return
        # Get output folder
        output_folder = build.get_output_folder_path()
        # Test if output folder exists
        if not os.path.isdir(output_folder):
            return
        output = {}
        for path, folders, files in os.walk(output_folder):
            current_path = path.replace(output_folder, "").strip("/")
            for folder in folders:
                output[folder.strip("/")] = {}
            if current_path != '':
                output[current_path] = files
        return output



class DownloadFileController(rest.RestController):
    # CURL -x GET http://127.0.0.1:8080/v3/users/titilambert/myproject/builds/113/download/file?distro=centos_7&filename=grafana-1.9.0-1kaji0.2.noarch.rpm
    @wsme_pecan.wsexpose(File, unicode, unicode)
    def get(self, distro=None, filename=None):
        """Download one output file"""
        user = User.fetch(pecan.request.context['username'], sub_objects=False)
        if user is None:
            return None
        project_name = pecan.request.context['project_name']
        project = Project.fetch(user, project_name, sub_objects=False)
        if project is None:
            return None
        build_id = pecan.request.context['build_id']
        if build_id in ["latest"]:
            build_id = project.get_latest_build_id()
        build = Build.fetch(project, build_id, sub_objects=False)
        if build is None:
            return
        # Get options
        distro = pecan.request.GET.get('distro', None)
        filename = pecan.request.GET.get('filename', None)
        if distro not in supported_distros:
            distro = None
        # Get output folder
        output_folder = build.get_output_folder_path(distro)
        # Test if output folder exists
        if not os.path.isdir(output_folder):
            return None
        # Set headers
        headers = pecan.response.headers
        # Get one file
        if filename is not None and distro is not None:
            file_path = os.path.join(output_folder, filename)
            if not os.path.isfile(file_path):
                return None
            f = File(file_path)
            headers.add("Content-Disposition", str("attachment;filename=%s" % filename))
            return f
        return None



class DownloadArchiveController(rest.RestController):
    # CURL -x GET http://127.0.0.1:8080/v3/users/titilambert/kaji/builds/6/download
    # CURL -x GET http://127.0.0.1:8080/v3/users/titilambert/kaji/builds/6/download/archive?type=tgz
    # CURL -x GET http://127.0.0.1:8080/v3/users/titilambert/kaji/builds/6/download/archive?distro=debian_7
    @pecan.expose(generic=True)
    def get(self):
        """Download all files in one archive"""
        user = User.fetch(pecan.request.context['username'], sub_objects=False)
        if user is None:
            return None
        project_name = pecan.request.context['project_name']
        project = Project.fetch(user, project_name, sub_objects=False)
        if project is None:
            return None
        build_id = pecan.request.context['build_id']
        if build_id in ["latest"]:
            build_id = project.get_latest_build_id()
        build = Build.fetch(project, build_id, sub_objects=False)
        if build is None:
            return
        # Get options
        archive = pecan.request.GET.get('type', 'tgz')
        distro = pecan.request.GET.get('distro', None)
        if distro not in supported_distros:
            distro = None
        # Get output folder
        output_folder = build.get_output_folder_path(distro)
        # Test if output folder exists
        if not os.path.isdir(output_folder):
            return None

        # Set headers
        headers = pecan.response.headers
        # Prepare content type
        content_type = archive_types.get(archive, 'application/x-gzip')
        pecan.core.override_template(None, content_type)
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

        if build.package_name is None:
            return

        filename = project_name + "_%(package_version)s-%(package_release)s" % build.as_dict()
        if distro is not None:
            filename = filename + "-" + distro
        else:
            filename = filename + "-all_distros"
        filename = ".".join((filename, extension))
        headers.add("Content-Disposition", str("attachment;filename=%s" % filename))
        # returns
        return f.getvalue()


class DownloadController(rest.RestController):
    @pecan.expose()
    def _lookup(self, *remainder):
         return DownloadSubController(), remainder



class DownloadSubController(rest.RestController):
    file = DownloadFileController()
    archive = DownloadArchiveController()
