#!/usr/bin/python
from io import BytesIO
import os
import sys
import re

from docker import Client
from dulwich.client import TCPGitClient
from dulwich import index
from dulwich.repo import Repo

from dulwich.client import get_transport_and_path


cli = Client(base_url='unix://var/run/docker.sock', version="1.15")


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
    




docker_output_path = '/tmp/user/' + project_name
local_output_path = '/tmp/user2/' + project_name
container_tag = 'user/' + project_name
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





'''
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1.orig.tar.gz?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1.orig.tar.gz
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2_amd64.changes?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2_amd64.changes
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2.dsc?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2.dsc
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2.debian.tar.xz?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2.debian.tar.xz

WORKDIR /tmp
RUN ["dpkg-source", "-x", "adagios_1.6.1-2kaji0.2.dsc"]
WORKDIR adagios-1.6.1
RUN ["dpkg-buildpackage", "-us", "-uc"]
RUN yum install -y %(dependencies)s
RUN mkdir -p %(docker_output_path)s
CMD cp ../*.deb %(docker_output_path)s
''' % {'docker_output_path': docker_output_path,
       'dependencies': dependencies,
       'distro': distro}



f = BytesIO(dockerfile.encode('utf-8'))

output = cli.build(fileobj=f, rm=True, tag=container_tag, forcerm=True)

for i in output:
    dict_ = eval(i)
    if "stream" in dict_:
        print dict_["stream"]
    else:
        print i


commands = [
"""git clone git://172.17.42.1:9418/shinken shinken """,
"""cd shinken """,
"""yum install -y %s""" % dependencies,
"""easy_install sphinx""",
"""rpmbuild -ba shinken.spec --define "_sourcedir /shinken/" """,
"""ls /root/rpmbuild/BUILDROOT/shinken-2.0.3-3kaji0.2.x86_64/etc/ """,
]

command = "bash -c '%s'" % " && ".join(commands)

container = cli.create_container(container_tag, volumes=[local_output_path], command=command)

cli.start(container['Id'], binds={local_output_path: {'bind': docker_output_path, 'ro': False}})

for line in cli.attach(container['Id'], stdout=True, stderr=True, stream=True):
    print line


build_script = """

"""
commands = [
#"""git clone git://172.17.42.1:9418/shinken shinken""",
#"""git clone %s %s""" % (git_url, project_name),
#"""ping 172.17.42.1"""
#"""git clone git://172.17.42.1:9418/shinken %s""" % project_name,
#"""ls""",
#"""cd %s""" % project_name,
]


#for command in commands:
#    print "================"
#    print command
#    stream = cli.execute(container, command, detach=False, stream=True)
#    for line in stream:
#        print line
#    cli.wait(container)
#    for line in cli.execute(container['Id'], command, stream=True,  detach=False):
#        print line
cli.stop(container['Id'])
cli.remove_container(container['Id'])

#for image in cli.images(container_tag):
#    cli.remove_image(image['Id'])

