#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re
import logging
import shutil
import glob
import pecan
import timeit
from datetime import datetime
from urlparse import urlparse

from docker import Client

from deb_pkg_tools.control import parse_depends
from deb_pkg_tools.control import load_control_file

from joulupukki.worker.lib.packer import Packer


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
        self.config['ccache'] = self.config.get('ccache', False)
        self.config['version'] = ''
        self.config['release'] = ''
        self.config['name'] = ''
        self.config['source'] = ''

        deb_info = load_control_file(control_file_path)
        self.config['name'] = deb_info.get("Source")
        self.config['deps'] += parse_depends(deb_info.get('Build-Depends')).names

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
        volumes = ['/upstream']
        binds = {}

        commands.append("""apt-get update""")
        commands.append("""apt-get upgrade -y""")
        # Handle PPAs
        if self.config.get('ppa', []):
            commands.append("""apt-get install -y software-properties-common""")
            for ppa in self.config.get('ppa', []):
                commands.append("""add-apt-repository %s""" % ppa)
	    commands.append("""apt-get update -y""")
            commands.append("""apt-get upgrade -y""")
        # Handle ccache
        if pecan.conf.ccache_path is not None and self.config.get('ccache', False):
            self.logger.info("CCACHE is enabled")
            ccache_path = os.path.join(pecan.conf.ccache_path,
                                       self.builder.build.user.username,
                                       self.config['name'],
                                       self.config['distro'].replace(":", "_"))
            if not os.path.exists(ccache_path):
                try:
                    os.makedirs(ccache_path)
                except Exception as exp:
                    self.logger.error("CCACHE folder creation error: %s", exp)
                    return False
            volumes.append('/ccache')
            binds[ccache_path] = {"bind": "/ccache"}
            commands.append("""apt-get install -y ccache""")
            commands.append("""export PATH=/usr/lib/ccache:$PATH""")
            commands.append("""export CCACHE_DIR=/ccache""")
        # Handle build dependencies
        if self.config['deps']:
            commands.append("""apt-get install -y %s""" % " ".join(self.config['deps']))
        # Handle python build dependencies
        if self.config['deps_pip']:
            commands.append("""apt-get install -y python-setuptools""")
            commands.append("""easy_install %s""" % " ".join(self.config['deps_pip']))

        # Prepare sources
        commands.append("""mkdir -p /sources""")
        commands.append("""rsync -rlptD --exclude '.git' --exclude 'debian' /%s/ /sources/%s""" % (docker_source_root_folder, self.config['name']))
        # Get the correct debian folder
        commands.append("""rsync -rlptD /%s/%s/ /sources/%s/debian""" % (docker_source_root_folder, self.config['debian'], self.config['name']))
        # Create original archive
        commands.append("""(cd /sources/%s && debian/rules get-orig-source || tar -C /sources -czf /sources/%s %s )""" % (self.config['name'], self.config['source'], self.config['name']))

        # Build
        commands.append("""cd /sources/%s """ % self.config['name'])
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
        start_time = timeit.default_timer()
        try:
            self.container = self.cli.create_container(self.container_tag, command=command, volumes=volumes)
        except Exception as exp:
            self.logger.error("Error launching docker container: %s", exp)
            return False
        local_source_folder = os.path.join(self.folder, "sources")
        binds[local_source_folder] = {"bind": "/upstream", "ro": True}
        toto = self.cli.start(self.container['Id'], binds=binds)

        for line in self.cli.attach(self.container['Id'], stdout=True, stderr=True, stream=True):
            self.logger.info(line.strip())
        # Stop container
        self.cli.stop(self.container['Id'])
        elapsed = timeit.default_timer() - start_time
        self.set_build_time(elapsed)
        self.logger.info("DEB Build finished in %ds", elapsed)
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
