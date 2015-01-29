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

cli = Client(base_url='unix://var/run/docker.sock', version="1.15")


def rpmpacker(git_folder, git_url, config, raw_distro):
    # Distro
    deps_pip = config.get("deps_pip")
    spec_file = config.get("spec")
    distro = supported_distros.get(raw_distro)

    # TODO find a better output folder
    output_folder = os.path.join(git_folder, "../__packer__output")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Browse
    deps = []
    raw_sources = []
    deps_pattern = re.compile("^buildrequires *:(.*)", re.IGNORECASE)
    version_pattern = re.compile("^version *:(.*)", re.IGNORECASE)
    name_pattern = re.compile("^name *:(.*)", re.IGNORECASE)
    release_pattern = re.compile("^release *:(.*)", re.IGNORECASE)
    sources_pattern = re.compile("^source[0-9]* *:(.*)", re.IGNORECASE)

    spec_file_path = os.path.join(git_folder, spec_file)
    for line in open(spec_file_path, 'r'):
        # Get rpm dependencies
        match = deps_pattern.match(line)
        if match:
            deps.append(match.group(1).strip())
        # Get rpm sources names
        match = sources_pattern.match(line)
        if match:
            raw_sources.append(match.group(1).strip())
        # Get version
        match = version_pattern.match(line)
        if match:
            version = match.group(1).strip()
        # Get release
        match = release_pattern.match(line)
        if match:
            release = match.group(1).strip()
        # Get name
        match = name_pattern.match(line)
        if match:
            name = match.group(1).strip()

    sources = []
    for source in raw_sources:
        source_p = urlparse(source)
        source = source_p.path.rsplit('/', 1)[-1]
        source = source.replace("%{release}", release)
        source = source.replace("%{version}", version)
        source = source.replace("%{name}", name)
        sources.append(source)

    # TODO Impossible to get more than one source
    if len(sources) != 1:
        # BAD number of source
        return
    source = sources[0]

    container_tag = "packer"
    dependencies = " ".join(deps)

    # DOCKER FILE TEMPLATE
    dockerfile = '''
    FROM %(distro)s
    RUN apt-get update
    RUN apt-get upgrade -y
    RUN apt-get install -y devscripts debianutils debhelper build-essential git-core tar
    ''' % {'distro': distro}



    dockerfile= '''
    FROM %(distro)s
    RUN yum upgrade -y
    RUN yum install git rpm-build tar -y
    CMD ["/bin/sh"]
    ''' % {'distro': distro}



    f = BytesIO(dockerfile.encode('utf-8'))

    # BUILD
    output = cli.build(fileobj=f, rm=True, tag=container_tag, forcerm=True)

    for i in output:
        dict_ = eval(i)
        if "stream" in dict_:
            print dict_["stream"]
        else:
            print i

    # RUN
    folder_name = name + "-" + version
    commands = [

    """git clone %s %s --depth=1""" % (git_url, folder_name),
    # TODO checkout branch or commit
    """rm -rf %s/.git""" % folder_name,
    """tar czf %s %s""" % (source, folder_name),
    ]
    
    if dependencies:
        commands.append("""yum install -y %s""" % dependencies)

    if deps_pip:
        commands.append("""yum install -y python-setuptools""")
        commands.append("""easy_install %s""" % " ".join(deps_pip))

    commands.append("""cd %s && rpmbuild -ba %s --define "_sourcedir /" """ % (folder_name, spec_file))

    command = "bash -c '%s'" % " && ".join(commands)

    container = cli.create_container(container_tag, command=command)

    cli.start(container['Id'])

    for line in cli.attach(container['Id'], stdout=True, stderr=True, stream=True):
        print line
    # Stop container
    cli.stop(container['Id'])


    # Get RPMS
    rpms_raw = cli.copy(container['Id'], "/root/rpmbuild/RPMS")
    rpms_tar_file_name = os.path.join(output_folder, "rpms.tar")
    print rpms_tar_file_name
    rpms_tar_file = open(rpms_tar_file_name, "w")
    rpms_tar_file.write(rpms_raw.read())
    rpms_tar_file.close()
    # Get SRPM
    srpms_raw = cli.copy(container['Id'], "/root/rpmbuild/SRPMS")
    srpms_tar_file_name = os.path.join(output_folder, "srpms.tar")
    srpms_tar_file = open(srpms_tar_file_name, "w")
    srpms_tar_file.write(srpms_raw.read())
    srpms_tar_file.close()

    # Delete container
    cli.remove_container(container['Id'])

    # Untar RPM
    rpms_tar = tarfile.open(rpms_tar_file_name)
    rpms_tar.extractall(output_folder)
    rpms_tar.close()
    # Untar SRPM
    srpms_tar = tarfile.open(srpms_tar_file_name)
    srpms_tar.extractall(output_folder)
    srpms_tar.close()


    # Remove images
    try:
        for image in cli.images(container_tag):
            cli.remove_image(image['Id'])
    except Exception:
        pass
