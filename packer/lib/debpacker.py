#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re
import logging
from urlparse import urlparse

from docker import Client


from distros import supported_distros

from deb_pkg_tools.control import parse_depends
from deb_pkg_tools.control import load_control_file

cli = Client(base_url='unix://var/run/docker.sock', version="1.15")


def debpacker(git_folder, git_url, config, raw_distro):
    # Get config
    deps_pip = config.get("deps_pip")
    debian = config.get("debian")
    distro = supported_distros.get(raw_distro)

    control_file_path = os.path.join(git_folder, debian, "control")
    changelog_file_path = os.path.join(git_folder, debian, "changelog")

    # TODO find a better output folder
    output_folder = os.path.join(git_folder, "../__packer__output")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Browse
    deb_info = load_control_file(control_file_path)
    name = deb_info.get("Source")

    deps = parse_depends(deb_info.get('Build-Depends'))
    deps = tuple(deps.names)
    dependencies = " ".join(deps)
    

    version_release_pattern = re.compile("[^ ]* \(([^ ]*)\) .*")
    with open(changelog_file_path, 'r') as f:
        first_line = f.readline()

    match = version_release_pattern.match(first_line)

    if not match:
        return

    version_release = match.group(1)
    version, release = version_release.split("-", 1)

    container_tag = "packer"

    # DOCKER FILE TEMPLATE
    dockerfile = '''
    FROM %(distro)s
    RUN apt-get update
    RUN apt-get upgrade -y
    RUN apt-get install -y devscripts debianutils debhelper build-essential git-core tar
    ''' % {'distro': distro}


    f = BytesIO(dockerfile.encode('utf-8'))

    # BUILD
    output = cli.build(fileobj=f, rm=True, tag=container_tag, forcerm=True)

    for i in output:
        dict_ = eval(i)
        if "stream" in dict_:
            print dict_["stream"].strip()
        else:
            print i

    # RUN
    folder_name = name
    source = name + "_" + version + ".orig.tar.gz"
    commands = [

    """git clone %s %s --depth=1""" % (git_url, folder_name),
    # TODO checkout branch or commit
    """rm -rf %s/.git""" % folder_name,
    """tar czf %s %s""" % (source, folder_name),
    ]
    
    if dependencies:
        commands.append("""apt-get install -y %s""" % dependencies)

    if deps_pip:
        commands.append("""apt-get install -y python-setuptools""")
        commands.append("""easy_install %s""" % " ".join(deps_pip))

    commands.append("""cd %s && dpkg-buildpackage -uc -us""" % folder_name)
    commands.append("""cd /""")
    commands.append("""mkdir output""")
    commands.append("""mv *.orig.tar* *.debian.tar* *deb *changes *dsc output""")

    command = "bash -c '%s'" % " && ".join(commands)

    container = cli.create_container(container_tag, command=command)

    cli.start(container['Id'])

    for line in cli.attach(container['Id'], stdout=True, stderr=True, stream=True):
        print line.strip()
    # Stop container
    cli.stop(container['Id'])

    # Get debs
    debs_raw = cli.copy(container['Id'], "/output")
    debs_tar_file_name = os.path.join(output_folder, "debs.tar")
    debs_tar_file = open(debs_tar_file_name, "w")
    debs_tar_file.write(debs_raw.read())
    debs_tar_file.close()

    # Delete container
    cli.remove_container(container['Id'])

    # Untar DEB
    debs_tar = tarfile.open(debs_tar_file_name)
    debs_tar.extractall(output_folder)
    debs_tar.close()

    # Remove images
    try:
        for image in cli.images(container_tag):
            cli.remove_image(image['Id'])
    except Exception:
        pass
