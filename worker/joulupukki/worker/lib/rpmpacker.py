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
from urlparse import urlparse
from collections import OrderedDict
from datetime import datetime

from docker import Client
import rpm

from joulupukki.worker.lib.packer import Packer


class RpmPacker(Packer):

    def parse_specdeb(self):
        # Get spec infos
        self.logger.info("Find informations from spec file")
        spec_file_path = os.path.join(self.folder,
                                      'sources',
                                       self.config['root_folder'],
                                       self.config['spec'])

        # Prepare datas
        self.config['deps'] = self.config.get('deps', [])
        self.config['deps_pip'] = self.config.get('deps_pip', [])
        self.config['ccache'] = self.config.get('ccache', False)
        self.config['version'] = ''
        self.config['release'] = ''
        self.config['name'] = ''
        self.config['source'] = ''
        self.config['sources'] = ''
        self.config['source_folder'] = ''
        raw_sources = []
        # Prepare spec datas
        mapping = {1000: 'name',
                   1001: 'version',
                   1002: 'release',
                   1049: 'deps',
                   1018: 'sources',
                  }
        spec = rpm.ts().parseSpec(spec_file_path)
        # Get spec data
        for id_, attr_name in mapping.items():
            if isinstance(self.config.get(attr_name), list):
                self.config[attr_name] += spec.sourceHeader[id_]
            else:
                self.config[attr_name] = spec.sourceHeader[id_]
        # Get only the first source
        self.config['source'] = self.config['sources'][0]
        # Try to find the name of the folder which rpmbuild needs to find
        # in the source tarball
        match = re.match(".*\/BUILD\'\nrm -rf '(.*)'", spec.prep)
        if match:
            self.config['source_folder'] = match.group(1)
        else:
            self.config['source_folder'] = self.config['name'] + "-" + self.config['version']

        # Log informations
        self.logger.info("Name: %(name)s", self.config)
        self.logger.info("Source: %(source)s", self.config)
        self.logger.info("Source folder: %(source_folder)s", self.config)
        self.logger.info("Version: %(version)s", self.config)
        self.logger.info("Release: %(release)s", self.config)
        self.logger.info("Buildrequires: %s", ", ".join(self.config['deps']))
        return True


    def docker_build(self):
        self.logger.info("Dockerfile preparation")
        # DOCKER FILE TEMPLATE
        # Create and user an user "builder"
        dockerfile= '''
        FROM %(distro)s
        RUN yum upgrade -y
        RUN yum install rpm-build tar rsync -y
        ''' % self.config
        f = BytesIO(dockerfile.encode('utf-8'))

        # BUILD
        self.logger.info("Docker Image Building")
        try:
            output = self.cli.build(fileobj=f, rm=True, tag=self.container_tag, forcerm=True)
        except Exception as exp:
            self.logger.error("Error launching docker container: %s", exp)
            return False
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
        docker_spec_file = os.path.join("/sources/%s" % self.config['source_folder'], self.config['spec'])

        commands = []
        volumes = ['/upstream']
        binds = {}

        commands.append("""yum upgrade -y""")
        commands.append("""mkdir -p /sources""")
        commands.append("""rsync -rlptD --exclude '.git' /%s/ /sources/%s""" % (docker_source_root_folder, self.config['source_folder']))
        commands.append("""tar -C /sources -cf /sources/%s %s""" % (self.config['source'], self.config['source_folder']))

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
            commands.append("""yum install -y ccache""")
            commands.append("""export PATH=/usr/lib64/ccache:$PATH""")
            commands.append("""export CCACHE_DIR=/ccache""")
        # Handle build dependencies
        if self.config['deps']:
            commands.append("""yum install -y %s""" % " ".join(self.config['deps']))
        # Handle python build dependencies
        if self.config['deps_pip']:
            commands.append("""yum install -y python-setuptools""")
            commands.append("""easy_install %s""" % " ".join(self.config['deps_pip']))
        # snapshot
        if self.builder.build.snapshot:
            version = self.config['version']
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            if self.builder.build.commit:
                commit = self.builder.build.commit[:7]
                self.config['release'] = date + "~git" + commit
            else:
                self.config['release'] = date
            commands.append(""" sed -i "s/^Release:.*/Release: %s/g" %s """ % (self.config['release'], docker_spec_file))

        # Build
        commands.append("""rpmbuild -ba /%s --define "_sourcedir /sources" """ % docker_spec_file)
        # Finish command preparation
        command = "bash -c '%s'" % " && ".join(commands)
        self.logger.info("Build command: %s", command)

        # RUN
        self.logger.info("RPM Build starting")
        start_time = timeit.default_timer()
        self.container = self.cli.create_container(self.container_tag, command=command, volumes=volumes)
        local_source_folder = os.path.join(self.folder, "sources")
        binds[local_source_folder] = {"bind": "/upstream", "ro": True}
        self.cli.start(self.container['Id'], binds=binds)

        for line in self.cli.attach(self.container['Id'], stdout=True, stderr=True, stream=True):
            self.logger.info(line.strip())
        # Stop container
        self.cli.stop(self.container['Id'])
        elapsed = timeit.default_timer() - start_time
        self.set_build_time(elapsed)
        self.logger.info("RPM Build finished in %ds", elapsed)
        # Get exit code
        if self.cli.wait(self.container['Id']) != 0:
            return False
        else:
            return True

    def get_output(self):
        # Get RPMS from the container
        self.logger.info("Get RPM files")
        rpms_raw = self.cli.copy(self.container['Id'], "/root/rpmbuild/RPMS")
        rpms_tar = tarfile.open(fileobj=BytesIO(rpms_raw.read()))
        rpms_tar.extractall(self.job_tmp_folder)
        rpms_tar.close()
        # Get SRPM from the container
        self.logger.info("Get SRPM files")
        srpms_raw = self.cli.copy(self.container['Id'], "/root/rpmbuild/SRPMS")
        srpms_tar = tarfile.open(fileobj=BytesIO(srpms_raw.read()))
        srpms_tar.extractall(self.job_tmp_folder)
        srpms_tar.close()
        # move files to folder output
        for rpm in glob.glob(os.path.join(self.job_tmp_folder, "*/*.rpm")):
            shutil.move(rpm, self.folder_output)
        for rpm in glob.glob(os.path.join(self.job_tmp_folder, "*/*/*.rpm")):
            shutil.move(rpm, self.folder_output)
        
        self.logger.info("RPM and SRPM files deposed in output folder")
        return True
