#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re
import logging
import shutil
import glob
from urlparse import urlparse

from docker import Client

from deb_pkg_tools.control import parse_depends
from deb_pkg_tools.control import load_control_file

from packer.lib.distros import supported_distros

class DebPacker(object):

    def __init__(self, builder, config):
        self.logger = builder.logger
        self.dlogger = builder.dlogger
        self.config = config
        self.git_url = builder.git_url
        self.cli = builder.cli

        self.folder_output_tmp = os.path.join(builder.folder,
                                              'tmp',
                                              self.config['distro'])
        self.folder_output = os.path.join(builder.folder_output,
                                          self.config['distro'])
        os.makedirs(self.folder_output)
        self.folder = builder.folder


        self.container_tag = "packer"
        self.container = None

    def run(self):
       # import ipdb;ipdb.set_trace()

        self.parse_spec()
        self.docker_build()
        self.docker_run()
        self.get_rpms()
        self.clean_up()

    def parse_spec(self):
        # Get debian infos
        self.logger.info("Find informations from spec file")

        control_file_path = os.path.join(self.folder,
                                         'git',
                                         self.config['root_folder'],
                                         self.config['debian'],
                                         'control')
        changelog_file_path = os.path.join(self.folder,
                                           'git',
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
            return

        version_release = match.group(1)
        self.config['version'], self.config['release'] = version_release.split("-", 1)
        self.config['source'] = self.config['name'] + "_" + self.config['version'] + ".orig.tar.gz"

        # Log informations
        self.logger.info("Name: %(name)s", self.config)
        self.logger.info("Source: %(source)s", self.config)
        self.logger.info("Version: %(version)s", self.config)
        self.logger.info("Release: %(release)s", self.config)
        self.logger.info("Builddepends: %s", ", ".join(self.config['deps']))


    def docker_build(self):
        self.logger.info("Dockerfile preparation")
        dependencies = " ".join(self.config['deps'])
        # DOCKER FILE TEMPLATE
        # Create and user an user "builder"
        dockerfile = '''
        FROM %(distro)s
        RUN apt-get update
        RUN apt-get upgrade -y
        RUN apt-get install -y devscripts debianutils debhelper build-essential git-core tar
        ''' % self.config
        f = BytesIO(dockerfile.encode('utf-8'))

        # BUILD
        self.logger.info("Docker Image Building")
        output = self.cli.build(fileobj=f, rm=True, tag=self.container_tag, forcerm=True)
        # log output
        for i in output:
            dict_ = eval(i)
            if "stream" in dict_:
                self.dlogger.info(dict_["stream"].strip())
            else:
                if 'error' in dict_:
                    self.dlogger.info(dict_['errorDetail']['message'].strip())
                else:
                    self.dlogger.info(str(i))
        self.logger.info("Docker Image Built")
            

    def docker_run(self):
        # PREPARE BUILD COMMAND
        docker_source_root_folder = os.path.join('upstream', self.config['root_folder'])
        commands = [
        """mkdir -p /sources""",
        """git clone %s upstream""" % self.git_url,
        """cd upstream""",
        """git checkout %s""" % self.config['branch'],
        """rm -rf .git""",
        """ls /sources""",
        """cp -r /%s /sources/%s""" % (docker_source_root_folder, self.config['name']), 
        """cd /sources/""",
        """tar czf /sources/%s %s""" % (self.config['source'], self.config['name']),
        """ls /sources/""",
        ]

        # Handle build dependencies
        if self.config['deps']:
            commands.append("""apt-get install -y %s""" % " ".join(self.config['deps']))
        # Handle python build dependencies
        if self.config['deps_pip']:
            commands.append("""apt-get install -y python-setuptools""")
            commands.append("""easy_install %s""" % " ".join(self.config['deps_pip']))
        # Build
        commands.append("""cd %s && dpkg-buildpackage -uc -us""" % self.config['name'])
        commands.append("""cd .. && mkdir /output""")
        commands.append("""mv *.orig.tar* *.debian.tar* *deb *changes *dsc /output""")
        # Finish command preparation
        command = "bash -c '%s'" % " && ".join(commands)
        self.logger.info("Build command: %s", command)

        # RUN
        self.logger.info("DEB Build starting")
        self.container = self.cli.create_container(self.container_tag, command=command)
        self.cli.start(self.container['Id'])

        for line in self.cli.attach(self.container['Id'], stdout=True, stderr=True, stream=True):
            self.dlogger.info(line.strip())
        # Stop container
        self.cli.stop(self.container['Id'])
        self.logger.info("DEB Build finished")


    def get_rpms(self):
        # Get debs from the container
        debs_raw = self.cli.copy(self.container['Id'], "/output")
        debs_tar = tarfile.open(fileobj=BytesIO(debs_raw.read()))
        debs_tar.extractall(self.folder_output_tmp)
        debs_tar.close()
        # move files to folder output
        for file_ in glob.glob(os.path.join(self.folder_output_tmp, "output/*")):
            shutil.move(file_, self.folder_output)

        
        self.logger.info("DEBS files deposed in output folder")


    def clean_up(self):
        # Delete container
        self.logger.debug('Deleting docker container: %s', self.container['Id'])
        self.cli.remove_container(self.container['Id'])

        # Remove images
        for image in self.cli.images(self.container_tag):
            try:
                self.logger.debug('Deleting docker image: %s', image['Id'])
                self.cli.remove_image(image['Id'])
            except Exception as error:
                self.logger.debug('Cannot deleting docker image: %s'
                                  ' - Error: %s', image['Id'], error)


