import os
import subprocess

from joulupukki.worker.lib.packer import Packer
from joulupukki.common.logger import get_logger, get_logger_job
from joulupukki.common.datamodel.job import Job

class OsxPacker(object):
    def __init__(self, builder, config):
        self.config = config
        self.builder = builder
        self.distro = "osx"
        
        self.source_url = builder.source_url
        self.source_type = builder.source_type
        self.folder = builder.folder

        job_data = {
            'distro': self.distro,
            'username': self.builder.build.username,
            'project_name': self.builder.build.project_name,
            'build_id': self.builder.build.id_,
        }
        self.job = Job(job_data)
        self.job.create()
        self.folder_output = self.job.get_folder_output()

        self.job_tmp_folder = self.job.get_folder_tmp()

        if not os.path.exists(self.folder_output):
            os.makedirs(self.folder_output)
        if not os.path.exists(self.job_tmp_folder):
            os.makedirs(self.job_tmp_folder)

        self.logger = get_logger_job(self.job)

    def set_status(self, status):
        self.job.set_status(status)

    def set_build_time(self, build_time):
        self.job.set_build_time(build_time)

    def run(self):
        steps = (
            ('setup', self.setup),
            ('compiling', self.compile_),
        )
        for step_name, step_function in steps:
            self.set_status(step_name)
            if step_function() is not True:
                self.logger.debug("Task failed during step: %s", step_name)
                self.set_status('failed')
                return False
            # Save package name in build.cfg
            if (self.config.get('name') is not None and
                    self.builder.build.package_name is None):
                self.builder.build.package_name = self.config.get('name')
                self.builder.build._save()
        self.set_status('succeeded')
        return True

    def setup(self):
        # Installing dependencies
        dependencies = ["automake", "libtool", "gettext", "yasm", "autoconf",
                        "pkg-config", "qt5", "llvm --with-clang --with-asan"]
        for depen in dependencies:
            cmd_list = ["brew", "install"].append(depen.split(" "))
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()
            self.logger.debug(stdout)
            self.logger.info(stderr)
            if process.returncode:
                self.logger.error("Error in setup: %d" % process.returncode)
                return False
        return True

    def compile_(self):
        self.logger.info("Start compiling")
        # Compiling ring-daemon
        cmds = [
            'echo "Deamon"',
            'git clone https://gerrit-ring.savoirfairelinux.com/ring-daemon daemon',
            'cd deamon',
            'cd contrib',
            'mkdir native',
            'cd native',
            '../bootstrap',
            'make -j3',
            'cd ../../',
            './autogen.sh && configure --without-alsa --without-pulse --without-dbus --prefix=%(prefix_path)s',
            'make install -j',
            'cd ..',
            'echo "LRC"',
            'export CMAKE_PREFIX=/usr/Cellar/qt5/5.4.0',
            'git clone git://anongit.kde.org/libringclient.git libringclient',
            'cd libringclient',
            'mkdir build',
            'cd build',
            'cmake .. -DCMAKE_INSTALL_PREFIX=%(prefix_path) -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=/usr/local/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/usr/local/opt/llvm/bin/clang++',
            'make install',
            'cd ..',
            'echo "Client"',
            'git clone https://gerrit-ring.savoirfairelinux.com/ring-client-macosx',
            'cd ring-client-macosx',
            'mkdir build && cd build',
            'export CMAKE_PREFIX_PATH=/usr/local/Cellar/qt5/5.4.0',
            'cmake ../ -DCMAKE_INSTALL_PREFIX=%(prefix_path)s',
            'make install -j',
            'cpack -G DragNDrop Ring',
        ]

        for cmd in cmds:
            cmd_args_list = cmd.split(" ")
            self.logger.info("Cmd: %s" % cmd_args_list)
            process = subprocess.Popen(
                cmd_args_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            self.logger.debug(stdout)
            self.logger.info(stderr)
            if process.returncode:
                self.logger.error("Error in setup: %d" % process.returncode)
                return False
        return True



    def parse_specdeb(self):
        pass
