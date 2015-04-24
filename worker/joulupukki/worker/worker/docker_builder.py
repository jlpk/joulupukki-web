from builder import Builder

from joulupukki.common.distros import distro_templates
from joulupukki.worker.lib.rpmpacker import RpmPacker
from joulupukki.worker.lib.debpacker import DebPacker

import logging


class DockerBuilder(Builder):
    def run(self):
        failed = False
        distro_type = distro_templates.get(self.distro_name)
        packer_class = globals().get(distro_type.capitalize() + 'Packer')
        packer = packer_class(self, self.build_conf)
        packer.set_status('building')
        self.logger.info("Packaging starting for %s", self.distro_name)
        if packer.run() is True:
            packer.set_status('succeeded')
            logging.info("Packaging finished for %s", self.distro_name)
        else:
            packer.set_status('failed')
            failed = True
            logging.info("Packaging finished for %s", self.distro_name)

        if failed:
            self.build.set_status('failed')
            return False
