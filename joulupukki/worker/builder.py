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
        self.folder_output = os.path.join(self.folder, 'output')
        self.folder_git = os.path.join(self.folder, 'git')
        os.makedirs(self.folder)
        os.makedirs(self.folder_output)
        # Prepare logger
        self.logger = get_logger(self.uuid)
        self.dlogger = get_logger_docker(self.uuid)

    def git_clone(self):
        self.logger.info("Cloning")
        # Clone repo
        repo = git.Repo.clone_from(self.git_url, self.folder_git)
        # Get branch/tag if set
        if self.branch is not None:
            for ref in repo.refs:
                if ref.name == self.branch:
                    repo.head.reference = repo.commit(ref)
                if ref.name == "origin/" + self.branch:
                    repo.head.reference = repo.commit(ref)
        # Get commit if set
        if self.commit is not None:
            repo.head.reference = repo.commit(commit)
        # Build tree
        repo.head.reset(index=True, working_tree=True)
        self.logger.info("Cloned")

    def run_packer(self, packer_conf, root_folder):
        # DOCKER
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
            packer.run()
            self.status['builds'][build_conf['distro']] = 'succeeded'

    def run(self):
        # GIT
        self.logger.info("Started")
        self.status['task'] = 'clonning'
        self.git_clone()
        
        # YAML
        self.logger.debug("Read .packer.yml")
        self.status['task'] = 'reading'
        global_packer_conf_file_name = os.path.join(self.folder_git, ".packer.yml")
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

        # Delete tmp git folder
        self.logger.info("Tmp folder deleting")
        if os.path.exists(os.path.join(self.folder,'tmp')):
            shutil.rmtree(os.path.join(self.folder,'tmp'))
        shutil.rmtree(self.folder_git)
        self.logger.info("Tmp folder deleted")
        self.status['task'] = 'finished'
