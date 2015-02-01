from threading import Thread
import glob
import os
import shutil

import pecan
import git
import yaml

from joulupukki.lib.rpmpacker import RpmPacker
from joulupukki.lib.debpacker import DebPacker
from joulupukki.lib.distros import supported_distros, distro_templates
from joulupukki.lib.logger import get_logger, get_logger_docker


from docker import Client
import re


#from urllib.parse import urlparse
import urlparse

"""
scheduled
clonning
dispatching
finished
"""

class Builder(Thread):
    def __init__(self, data):
        Thread.__init__(self, name=data.uuid)
        self.git_url = data.git_url
        self.branch = data.branch
        self.commit = data.commit
        self.uuid = data.uuid

        # Create docker client
        self.cli = Client(base_url='unix://var/run/docker.sock', version="1.15")
        # Set status
        self.status = {'task': 'scheduled',
                       'builds': {}}
        # Set folders
        self.folder = os.path.join(pecan.conf.tmp_path, self.uuid)
        self.folder_git = os.path.join(self.folder, 'git')
        os.makedirs(self.folder)
        # Prepare logger
        self.logger = get_logger(self.uuid)

    def git_clone(self):
        self.logger.info("Cloning")
        # Reworking url to handle password
        url_splitted = urlparse.urlsplit(self.git_url)
        username = url_splitted.username
        if username is None:
            username = 'anonymous'
        password = url_splitted.username
        if password is None:
            password = 'anonymous'
        url_data = [d for d in list(url_splitted)]
        new_netloc = username + ":" + password + "@" + url_data[1]
        url_data[1] = new_netloc
        git_url = urlparse.urlunsplit(url_data)
        # Clone repo
        try:
            repo = git.Repo.clone_from(git_url, self.folder_git)
        except Exception as exp:
            self.logger.error("Clonning error: %s", exp)
            return False
        branch_found = True
        # Get branch/tag if set
        if self.branch is not None:
            branch_found = False
            for ref in repo.refs:
                if ref.name == self.branch:
                    repo.head.reference = repo.commit(ref)
                    branch_found = True
                if ref.name == "origin/" + self.branch:
                    repo.head.reference = repo.commit(ref)
                    branch_found = True
        if branch_found is False:
            self.logger.error("Branch %s not found", self.branch)
            return False
        # Get commit if set
        if self.commit is not None:
            try:
                repo.head.reference = repo.commit(self.commit)
            except Exception as exp:
                self.logger.error("Bad commit: %s - %s", self.commit, exp)
                return False
        # Build tree
        repo.head.reset(index=True, working_tree=True)
        self.logger.info("Cloned")
        return True

    def run_packer(self, packer_conf, root_folder):
        # DOCKER
        failed = False
        self.status['task'] = 'dispatching'
        for distro_name, build_conf in packer_conf.items():
            if distro_name not in supported_distros:
                self.logger.error("Distro %s not supported", distro_name)
                self.status['builds'][build_conf['distro']] = 'distro_not_supported'
                continue
            distro_type = distro_templates.get(distro_name)
            # Prepare distro configuration
            build_conf['distro'] = supported_distros.get(distro_name)
            build_conf['branch'] = self.branch
            build_conf['root_folder'] = root_folder
            # Launcher build
            self.logger.info("Distro %s is an %s distro", distro_name, distro_type)
            packer_class = globals().get(distro_type.capitalize() + 'Packer')
            packer = packer_class(self, build_conf)
            self.status['builds'][build_conf['distro']] = 'building'
            self.logger.info("Packaging starting for %s", distro_name)
            if packer.run() is True:
                self.status['builds'][build_conf['distro']] = 'succeeded'
                self.logger.info("Packaging finished for %s", distro_name)
            else:
                self.status['builds'][build_conf['distro']] = 'failed'
                self.logger.info("Packaging finished for %s", distro_name)
        if failed:
            return False
        self.logger.info("Packaging finished for all distros")

    def run(self):
        # GIT
        self.logger.info("Started")
        self.status['task'] = 'clonning'
        if self.git_clone() is True:
            # YAML
            self.logger.debug("Read .packer.yml")
            self.status['task'] = 'reading'
            global_packer_conf_file_name = os.path.join(self.folder_git, ".packer.yml")
            if os.path.exists(global_packer_conf_file_name):
                global_packer_conf_stream = file(global_packer_conf_file_name, 'r')
                global_packer_conf = yaml.load(global_packer_conf_stream)
                if 'include' in global_packer_conf:
                    for packer_file_glob in global_packer_conf.get("include"):
                        for packer_conf_file_name in glob.glob(os.path.join(self.folder_git, packer_file_glob)):
                            packer_conf_stream = file(packer_conf_file_name, 'r')
                            packer_conf = yaml.load(packer_conf_stream)
                            # Get root folder of this package
                            packer_conf_relative_file_name = packer_conf_file_name.replace(self.folder_git, "").strip("/")
                            root_folder = os.path.dirname(packer_conf_relative_file_name)
                            # Run packer
                            self.run_packer(packer_conf, root_folder)
                else:
                     self.run_packer(global_packer_conf, ".")
            else:
                self.logger.error("File .packer.yml not found")
                self.status['task'] = 'failed'
        else:
            self.status['task'] = 'failed'

        # Delete tmp git folder
        self.logger.info("Tmp folders deleting")
        if os.path.exists(os.path.join(self.folder,'tmp')):
            shutil.rmtree(os.path.join(self.folder,'tmp'))
        shutil.rmtree(self.folder_git)
        self.logger.info("Tmp folders deleted")
