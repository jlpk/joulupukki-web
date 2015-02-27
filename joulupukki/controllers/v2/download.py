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

from io import BytesIO
from joulupukki.controllers.v2.datamodel.build import Build, APIBuild
from joulupukki.controllers.v2.datamodel.user import User
from joulupukki.controllers.v2.datamodel.project import Project
from joulupukki.controllers.v2.datamodel.job import Job
from joulupukki.controllers.v2.jobs import JobsController


from joulupukki.lib.queues import build_tasks
from joulupukki.lib.distros import supported_distros, reverse_supported_distros


archive_types = {"zip": "application/zip",
                 "tgz": "application/x-gzip",
                }


class DownloadController(rest.RestController):
    # CURL -x GET http://127.0.0.1:8080/v2/titilambert/kaji/builds/6/download
    # CURL -x GET http://127.0.0.1:8080/v2/titilambert/kaji/builds/6/download?archive=tgz
    # CURL -x GET http://127.0.0.1:8080/v2/titilambert/kaji/builds/6/download?distro=debian_7
    @pecan.expose()
    def get(self):
        """Returns log of a specific distro."""
        project_name = pecan.request.context['project_name']
        user = User.fetch(pecan.request.context['username'])
        project = Project.fetch(user, project_name)
        build_id = pecan.request.context['build_id']
        if build_id in ["latest"]:
            build_id = project.get_latest_build()
        build = Build.fetch(project, build_id, full_data=True)
        # Get options
        archive = pecan.request.GET.get('archive', 'tgz')
        distro = pecan.request.GET.get('distro', None)
        if distro not in supported_distros:
            distro = None
        # Prepare content type
        content_type = archive_types.get(archive, 'application/x-gzip')
        pecan.core.override_template(None, content_type)
        # Get output folder
        output_folder = build.get_output_folder_path(distro)
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
        headers = pecan.response.headers
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


