#!/usr/bin/python
from io import BytesIO
from docker import Client

cli = Client(base_url='unix://var/run/docker.sock', version="1.15")


distros = {"ubuntu_12.04": "ubuntu:12.04",
           "ubuntu_14.04": "ubuntu:14.04",
           "debian_7": "debian:7",
           "debian_8": "debian:8",
           "centos_6": "centos:6",
           "centos_7": "centos:7",
          }
        

project_name = "adagios"
docker_output_path = '/tmp/user/' + project_name
local_output_path = '/tmp/user2/' + project_name
container_tag = 'user/' + project_name


dockerfile = '''
FROM ubuntu:14.04
RUN ["apt-get", "update"]
RUN ["apt-get", "upgrade", "-y"]
RUN ["apt-get", "install", "-y", "devscripts", "debianutils", "debhelper", "build-essential"]

RUN ["apt-get", "install", "-y", "git-core"]
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1.orig.tar.gz?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1.orig.tar.gz
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2_amd64.changes?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2_amd64.changes
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2.dsc?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2.dsc
ADD https://build.opensuse.org/source/home:kaji-project/adagios/adagios_1.6.1-2kaji0.2.debian.tar.xz?rev=20f972668e954e1a5c1de31ce485fdf5 /tmp/adagios_1.6.1-2kaji0.2.debian.tar.xz

WORKDIR /tmp
RUN ["dpkg-source", "-x", "adagios_1.6.1-2kaji0.2.dsc"]
WORKDIR adagios-1.6.1
RUN ["dpkg-buildpackage", "-us", "-uc"]
RUN mkdir -p %(docker_output_path)s
CMD cp ../*.deb %(docker_output_path)s
''' % {'docker_output_path': docker_output_path}



f = BytesIO(dockerfile.encode('utf-8'))

output = cli.build(fileobj=f, rm=True, tag=container_tag, forcerm=True, nocache=True)

for i in output:
    dict_ = eval(i)
    if "stream" in dict_:
        print dict_["stream"]
    else:
        print i

container = cli.create_container(container_tag, volumes=[local_output_path])

cli.start(container['Id'], binds={local_output_path: {'bind': docker_output_path, 'ro': False}})
cli.stop(container['Id'])
cli.remove_container(container['Id'])

for image in cli.images(container_tag):
    cli.remove_image(image['Id'])
