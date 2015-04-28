#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


from joulupukki.worker import VERSION
os.environ['PBR_VERSION'] = VERSION

import setuptools


setuptools.setup(
    setup_requires=['pbr'],
    version=VERSION,
    pbr=True,
)
