#!/usr/bin/python

from git import Repo
import os


project_name = "adagios"
gits_path = "gits"

project_path = os.path.join(gits_path, project_name)

repo = Repo.init(project_path, bare=False)




import ipdb;ipdb.set_trace()
