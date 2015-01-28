#!/usr/bin/python
from io import BytesIO
import os
import sys
import tarfile
import re

from docker import Client
from dulwich.client import TCPGitClient
from dulwich import index
from dulwich.repo import Repo

from dulwich.client import get_transport_and_path


cli = Client(base_url='unix://var/run/docker.sock', version="1.15")

# Distro
distros = {"ubuntu_12.04": "ubuntu:12.04",
           "ubuntu_14.04": "ubuntu:14.04",
           "debian_7": "debian:7",
           "debian_8": "debian:8",
           "centos_6": "centos:6",
           "centos_7": "centos:7",
          }
        

packer_tmp_path = "/tmp/packer"
if not os.path.exists(packer_tmp_path):
    os.mkdir(packer_tmp_path)

# Prepare git name and path
project_name = "shinken"
user_name = "user"
output_folder = os.path.join("/tmp", project_name)
git_local_path = os.path.join(packer_tmp_path, project_name)

# Prepare git client
git_address = "192.168.50.204"
git_port = 9418
git_client = TCPGitClient(git_address, git_port)
git_url = "git://%s:%s/%s" % (git_address, git_port, project_name)

# Fetch and checkout
if not os.path.exists(os.path.join(git_local_path, ".git")):
    local = Repo.init(git_local_path, mkdir=True)
else:
    local = Repo(git_local_path)

client, host_path = get_transport_and_path(git_url)
# Clone
remote_refs = client.fetch(host_path, local,
                           determine_wants=local.object_store.determine_wants_all,
                           progress=sys.stdout.write)

local["HEAD"] = remote_refs["HEAD"]
local._build_tree()

# Browse
deps = []
spec_pattern = re.compile("^buildrequires *:(.*)", re.IGNORECASE)
for root, dirs, files in os.walk(git_local_path):
    print root, dirs, files
    for file_ in files:
        # Get rpm dependencies
        if file_.endswith(".spec"):
            for line in open(os.path.join(root, file_), 'r'):
                match = spec_pattern.match(line)
                if match:
                    deps.append(match.group(1).strip())
        # Get deb dependencies
    

container_tag = "/".join((user_name, project_name))
dependencies = " ".join(deps)

distro = distros['ubuntu_14.04']
dockerfile = '''
FROM %(distro)s
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y devscripts debianutils debhelper build-essential git-core tar
''' % {'distro': distro}



distro = distros['centos_6']
dockerfile= '''
FROM %(distro)s
RUN yum upgrade -y
RUN yum install git rpm-build tar -y
CMD ["/bin/sh"]
''' % {'distro': distro}



f = BytesIO(dockerfile.encode('utf-8'))

output = cli.build(fileobj=f, rm=True, tag=container_tag, forcerm=True)

for i in output:
    dict_ = eval(i)
    if "stream" in dict_:
        print dict_["stream"]
    else:
        print i


commands = [
"""git clone git://172.17.42.1:9418/%s""" % project_name,
"""cd %s""" % project_name,
"""yum install -y %s""" % dependencies,
"""easy_install sphinx""",
"""rpmbuild -ba %s.spec --define "_sourcedir /%s/" """ % (project_name, project_name),
]

command = "bash -c '%s'" % " && ".join(commands)

container = cli.create_container(container_tag, command=command)

cli.start(container['Id'])

for line in cli.attach(container['Id'], stdout=True, stderr=True, stream=True):
    print line
# Stop container
cli.stop(container['Id'])


# Get RPMS
rpms_raw = cli.copy(container['Id'], "/root/rpmbuild/RPMS")
rpms_tar_file_name = os.path.join(output_folder, project_name + "_rpms.tar")
rpms_tar_file = open(rpms_tar_file_name, "w")
rpms_tar_file.write(rpms_raw.read())
rpms_tar_file.close()
# Get SRPM
srpms_raw = cli.copy(container['Id'], "/root/rpmbuild/SRPMS")
srpms_tar_file_name = os.path.join(output_folder, project_name + "_srpms.tar")
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
for image in cli.images(container_tag):
    cli.remove_image(image['Id'])
