#!/usr/bin/python

from dulwich.repo import Repo
from dulwich.server import DictBackend, TCPGitServer
import threading
import os


gits_path = "gits"
project_name = "shinken"


git_path = os.path.join(gits_path, project_name)

if not os.path.exists(git_path):
    os.mkdir(git_path)

if not os.path.exists(os.path.join(git_path, "HEAD")):
    repo = Repo.init_bare(git_path)
else:
    repo = Repo(git_path)

backend = DictBackend({'/' + project_name: repo})
dul_server = TCPGitServer(backend, '0.0.0.0')
server_address, server_port = dul_server.socket.getsockname()
print server_address, server_port
dul_server.serve()
#git clone git://127.0.0.1:9418/toto#

#threading.Thread(target=dul_server.serve).start()


