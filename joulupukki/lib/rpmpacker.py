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
from collections import OrderedDict
from datetime import datetime

from docker import Client

from joulupukki.lib.packer import Packer


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
        self.config['version'] = ''
        self.config['release'] = ''
        self.config['name'] = ''
        self.config['source'] = ''
        self.config['source_folder'] = ''
        raw_sources = []
        # Prepare patterns
        define_pattern = re.compile("^%define *([^ ]*) *([^ ]*)", re.IGNORECASE)
        deps_pattern = re.compile("^buildrequires *:(.*)", re.IGNORECASE)
        version_pattern = re.compile("^version *:(.*)", re.IGNORECASE)
        name_pattern = re.compile("^name *:(.*)", re.IGNORECASE)
        release_pattern = re.compile("^release *:(.*)", re.IGNORECASE)
        sources_pattern = re.compile("^source[0-9]* *:(.*)", re.IGNORECASE)
        source_folder_pattern = re.compile("^%setup [^n]*n ([^ ]*) ?.*")
        if not os.path.isfile(spec_file_path):
            self.logger.info("Spec file not found: %s", self.config['spec'])
            return False


        raw_defines = OrderedDict()
        for line in open(spec_file_path, 'r'):
            # Get defines
            match = define_pattern.match(line)
            if match:
                raw_defines[match.group(1)] = match.group(2).strip()
            # Get rpm dependencies
            match = deps_pattern.match(line)
            if match:
                self.config['deps'].append(match.group(1).strip())
            # Get rpm sources names
            match = sources_pattern.match(line)
            if match:
                raw_sources.append(match.group(1).strip())
            # Get version
            match = version_pattern.match(line)
            if match:
                self.config['version'] = match.group(1).strip()
            # Get release
            match = release_pattern.match(line)
            if match:
                self.config['release'] = match.group(1).strip()
            # Get name
            match = name_pattern.match(line)
            if match:
                self.config['name'] = match.group(1).strip()
            # get source name
            match = source_folder_pattern.match(line)
            if match:
                self.config['source_folder'] = match.group(1).strip()

        # Replace all defines
        defines = {}
        for define_name, define_value in raw_defines.items():
            defines[define_name] = re.sub(r"%{([^?}]*)}", r"%(\1)s", define_value) % defines

        for conf_name, config_value in self.config.items()[:]:
            if isinstance(config_value, str):
                tmp_ = re.sub(r"%{([^?}]*)}", r"%(\1)s", config_value)
                try:
                   self.config[conf_name] = re.sub(r"%{(\?[^}]*)}", r"%%{\1}", tmp_) % defines
                except Exception as exp:
                    self.logger.error("This string seems strange: %s", tmp_)
                    return False

        sources = []
        for source in raw_sources:
            source_p = urlparse(source)
            source = source_p.path.rsplit('/', 1)[-1]
            source = source.replace("%{release}", self.config['release'])
            source = source.replace("%{version}", self.config['version'])
            source = source.replace("%{name}", self.config['name'])
            sources.append(source)

        # TODO Impossible to get more than one source ??
        if len(sources) != 1:
            # BAD number of source
            return False
        self.config['source'] = sources[0]
        # Try to find the name of the folder which rpmbuild needs to find
        # in the source tarball
        if self.config['source_folder'] == '':
            self.config['source_folder'] = self.config['name'] + "-" + self.config['version']
            #ext_pattern = re.compile(r'^.*?[.](tar\.gz|tar\.bz2|tar\.zx|\w+)$')
            #match = ext_pattern.match(source)
            #if match:
            #    source_ext = match.group(1)
            #self.config['source_name'] = re.sub("." + source_ext + "$", "", source)

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
        docker_spec_file = os.path.join("/sources/%s" % self.config['source_folder'], self.config['spec'])
        commands = [
        """mkdir -p /sources""",
        """rsync -rlptD --exclude '.git' /%s/ /sources/%s""" % (docker_source_root_folder, self.config['source_folder']),
        """cd /sources/""",
        """tar cf /%s %s""" % (self.config['source'], self.config['source_folder']),
        ]
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
        commands.append("""rpmbuild -ba /%s --define "_sourcedir /" """ % docker_spec_file)
        # Finish command preparation
        command = "bash -c '%s'" % " && ".join(commands)
        self.logger.info("Build command: %s", command)

        # RUN
        self.logger.info("RPM Build starting")
        self.container = self.cli.create_container(self.container_tag, command=command, volumes=["/upstream"])
        local_source_folder = os.path.join(self.folder, "sources")
        self.cli.start(self.container['Id'],
                       binds={local_source_folder: {"bind": "/upstream",
                                                    "ro": True}})

        for line in self.cli.attach(self.container['Id'], stdout=True, stderr=True, stream=True):
            self.logger.info(line.strip())
        # Stop container
        self.cli.stop(self.container['Id'])
        self.logger.info("RPM Build finished")
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
