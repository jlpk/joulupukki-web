from threading import Thread
import glob

from joulupukki.worker.lib.rpmpacker import RpmPacker
from joulupukki.worker.lib.debpacker import DebPacker
from joulupukki.common.logger import get_logger, get_logger_docker
from joulupukki.common.distros import supported_distros, distro_templates

from docker import Client
import pecan


class Packer(Thread):
    def __init__(self, build):
        self.build = build
        self.source_url = build.source_url
        self.source_type = build.source_type
        self.branch = build.branch
        self.status = 'starting'
        self.user = build.user
        self.project = build.project
        self.id_ = str(build.id_)

        self.folder = build.get_folder_path()
        self.folder_source = build.get_source_folder_path()
    
        self.cli = Client(base_url='unix://var/run/docker.sock', version=pecan.conf.docker_version)

        self.logger = get_logger(self)

    def run_docker_packer(self, distro_name, build_conf, root_folder):
        # DOCKER
        failed = False
        # TODO Put all for content a sub thread :)

        # If forced_distro is set, we launch build only on 
        # the specified distro
        if self.build.forced_distro is not None and distro_name != self.build.forced_distro:
            return True
        # Check yml format
        if not isinstance(build_conf, dict):
            self.logger.error("Packer yml file seems malformated")
            self.build.set_status('bad_yml_file')
            return False
        # Check distro name
        if distro_name not in supported_distros:
            self.logger.error("Distro %s not supported", distro_name)
            # FIXME
            #self.set_status('distro_not_supported', distro_name)
            return False
        distro_type = distro_templates.get(distro_name)
        # Prepare distro configuration
        build_conf['distro'] = supported_distros.get(distro_name)
        build_conf['branch'] = self.branch
        build_conf['root_folder'] = root_folder
        # Launcher build
        self.logger.info("Distro %s is an %s distro", distro_name, distro_type)
        packer_class = globals().get(distro_type.capitalize() + 'Packer')
        self.logger.info(packer_class)
        packer = packer_class(self, build_conf)
        packer.set_status('building')
        self.logger.info("Packaging starting for %s", distro_name)
        if packer.run() is True:
            packer.set_status('succeeded')
            self.logger.info("Packaging finished for %s", distro_name)
        else:
            packer.set_status('failed')
            failed = True
            self.logger.info("Packaging finished for %s", distro_name)

        if failed:
            self.build.set_status('failed')
            return False
        return True
