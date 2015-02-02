supported_distros = {"ubuntu_12.04": "ubuntu:12.04",
                     "ubuntu_14.04": "ubuntu:14.04",
                     "debian_7": "debian:7",
                     "debian_8": "debian:8",
                     "centos_6": "centos:6",
                     "centos_7": "centos:7",
                    }

reverse_supported_distros = {v: k for k, v in supported_distros.items()}


distro_templates = {"ubuntu_12.04": "deb",
                    "ubuntu_14.04": "deb",
                    "debian_7": "deb",
                    "debian_8": "deb",
                    "centos_6": "rpm",
                    "centos_7": "rpm",
                   }
