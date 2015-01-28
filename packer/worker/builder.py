






import yaml

from threading import Thread

from packer.lib import giter

import pecan
import os

import logging


import shutil

from packer.lib.packager import packager


class Builder(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.git_url = data.git_url
        self.branch = data.branch
        self.commit = data.commit
        self.uuid = data.uuid

    def run(self):
        # GIT
        logging.debug("[build %s] started" % self.uuid)
        git_local_folder = os.path.join(pecan.conf.tmp_path, self.uuid)
        logging.debug("[build %s] cloning" % self.uuid)
        giter.clone(self.git_url, git_local_folder, self.branch, self.commit)
        logging.debug("[build %s] cloned" % self.uuid)

        # YAML
        logging.debug("[build %s] read .packer.yml" % self.uuid)
        packer_conf_file_name = os.path.join(git_local_folder, ".packer.yml")
        packer_conf_stream = file(packer_conf_file_name, 'r')
        packer_conf = yaml.load(packer_conf_stream)

        

        # DOCKER
        distros = packer_conf.get("distro")
        for distro in distros:
            packager(git_local_folder, self.git_url, packer_conf, distro)

        # Delete tmp git folder
        logging.debug("[build %s] tmp folder deleting" % self.uuid)
        shutil.rmtree(git_local_folder)
        logging.debug("[build %s] tmp folder deleted" % self.uuid)
