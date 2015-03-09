from pecan import make_app
from joulupukki.web import model

import logging

#from worker.manager import Manager
import sys

import signal





def setup_app(config):

    model.init_model()
    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)
    return app
