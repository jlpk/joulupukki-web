#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re
import logging
import shutil
import glob
from datetime import datetime
from urlparse import urlparse

from docker import Client

from deb_pkg_tools.control import parse_depends
from deb_pkg_tools.control import load_control_file

from joulupukki.lib.packer import Packer


class DebPacker(Packer):

    def parse_specdeb(self):
        # Get debian infos
        self.logger.info("Find informations from spec file")

        control_file_path = os.path.join(self.folder,
                                         'sources',
                                         self.config['root_folder'],
                                         self.config['debian'],
                                         'control')
        changelog_file_path = os.path.join(self.folder,
                                           'sources',
                                           self.config['root_folder'],
                                           self.config['debian'],
                                           'changelog')
        # Prepare datas
        self.config['deps'] = self.config.get('deps', [])
        self.config['deps_pip'] = self.config.get('deps_pip', [])
        self.config['version'] = ''
        self.config['release'] = ''
        self.config['name'] = ''
        self.config['source'] = ''

        deb_info = load_control_file(control_file_path)
        self.config['name'] = deb_info.get("Source")
        self.config['deps'] = parse_depends(deb_info.get('Build-Depends')).names

        version_release_pattern = re.compile("[^ ]* \(([^ ]*)\) .*")
        with open(changelog_file_path, 'r') as f:
            first_line = f.readline()

        match = version_release_pattern.match(first_line)

        if not match:
            return False

        version_release = match.group(1)
        self.config['version'], self.config['release'] = version_release.split("-", 1)
        # Clean version
        self.config['version'] = self.config['version'].split(":", 1)[-1]
        # Get source file
        self.config['source'] = self.config['name'] + "_" + self.config['version'] + ".orig.tar.gz"

        # Log informations
        self.logger.info("Name: %(name)s", self.config)
        self.logger.info("Source: %(source)s", self.config)
        self.logger.info("Version: %(version)s", self.config)
        self.logger.info("Release: %(release)s", self.config)
        self.logger.info("Builddepends: %s", ", ".join(self.config['deps']))
        return True


    def docker_build(self):
        self.logger.info("Dockerfile preparation")
        # DOCKER FILE TEMPLATE
        # Create and user an user "builder"
        dockerfile = '''
        FROM %(distro)s
        RUN apt-get update
        RUN apt-get upgrade -y
        RUN apt-get install -y devscripts debianutils debhelper build-essential tar rsync
        ''' % self.config
        f = BytesIO(dockerfile.encode('utf-8'))

        # BUILD
        self.logger.info("Docker Image Building")
        output = self.cli.build(fileobj=f, rm=True, tag=self.container_tag, forcerm=True)
        # log output
        for i in output:
            dict_ = eval(i)
            if "stream" in dict_:
                self.logger.info(dict_["stream"].strip())
            else:
                if 'error' in dict_:
                    self.logger.info(dict_['errorDetail']['message'].strip())
                else:
                    self.logger.info(str(i))
        self.logger.info("Docker Image Built")
        return True
            

    def docker_run(self):
        # PREPARE BUILD COMMAND
        docker_source_root_folder = os.path.join('upstream', self.config['root_folder'])
        commands = []
        commands.append("""mkdir -p /sources""")
        commands.append("""rsync -rlptD --exclude '.git' /%s /sources/%s""" % (docker_source_root_folder, self.config['name']))
        commands.append("""cd /sources/""")
        commands.append("""tar czf /sources/%s %s""" % (self.config['source'], self.config['name']))
        commands.append("""apt-get update""")
        commands.append("""apt-get upgrade -y""")

        # Handle build dependencies
        if self.config['deps']:
            commands.append("""apt-get install -y %s""" % " ".join(self.config['deps']))
        # Handle python build dependencies
        if self.config['deps_pip']:
            commands.append("""apt-get install -y python-setuptools""")
            commands.append("""easy_install %s""" % " ".join(self.config['deps_pip']))
        # Build
        commands.append("""cd %s """ % self.config['name'])
        if self.builder.build.snapshot:
            version = self.config['version']
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            if self.builder.build.commit:
                commit = self.builder.build.commit[:7]
                self.config['release'] = date + "~git" + commit
            else:
                self.config['release'] = date

            new_version = "-".join((version, self.config['release']))
            commands.append("""dch --newversion "%s" "Automatic nightly release" """ % new_version)
            commands.append("""dch --release --distribution "unstable" debian/changelog""")
        commands.append("""dpkg-buildpackage -uc -us""")
        commands.append("""cd .. """)
        commands.append("""mkdir /output""")
        commands.append("""mv *.orig.tar* *.debian.tar* *deb *changes *dsc /output""")
        # Finish command preparation
        command = "bash -c '%s'" % " && ".join(commands)
        self.logger.info("Build command: %s", command)

        # RUN
        self.logger.info("DEB Build starting")
        self.container = self.cli.create_container(self.container_tag, command=command, volumes=["/upstream"])
        local_source_folder = os.path.join(self.folder, "sources")
        toto = self.cli.start(self.container['Id'],
                       binds={local_source_folder: {"bind": "/upstream",
                                                    "ro": True}})

        for line in self.cli.attach(self.container['Id'], stdout=True, stderr=True, stream=True):
            self.logger.info(line.strip())
        # Stop container
        self.cli.stop(self.container['Id'])
        self.logger.info("DEB Build finished")
        # Get exit code
        if self.cli.wait(self.container['Id']) != 0:
            return False
        else:
            return True


    def get_output(self):
        # Get debs from the container
        debs_raw = self.cli.copy(self.container['Id'], "/output")
        debs_tar = tarfile.open(fileobj=BytesIO(debs_raw.read()))
        debs_tar.extractall(self.job_tmp_folder)
        debs_tar.close()
        # move files to folder output
        for file_ in glob.glob(os.path.join(self.job_tmp_folder, "output/*")):
            shutil.move(file_, self.folder_output)

        
        self.logger.info("DEBS files deposed in output folder")
        return True
