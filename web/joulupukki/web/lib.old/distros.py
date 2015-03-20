import pecan

supported_distros = {}
distro_templates = {}


for distro in pecan.conf.distros:
    supported_distros[distro[0]] = distro[1]
    distro_templates[distro[0]] = distro[2]

reverse_supported_distros = {v: k for k, v in supported_distros.items()}

