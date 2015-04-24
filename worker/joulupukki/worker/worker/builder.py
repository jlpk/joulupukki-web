from threading import Thread
from docker import Client

import pecan

class Builder(Thread, ):
    def __init__(self, distro_name, build_conf, root_folder, logger, build):
        self.source_url = build.source_url
        self.source_type = build.source_type

        self.distro_name = distro_name
        self.build_conf = build_conf
        self.root_folder = root_folder
        self.logger = logger
        self.build = build

        self.cli = Client(base_url='unix://var/run/docker.sock', version=pecan.conf.docker_version)

        self.folder = build.get_folder_path()

    def run(self):
        pass
