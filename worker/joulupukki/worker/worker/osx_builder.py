from builder import Builder

from joulupukki.worker.lib.osxpacker import OsxPacker

import logging


class OsxBuilder(Builder):
    def run(self):
        failed = False
        packer = OsxPacker(self, self.build_conf)
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
