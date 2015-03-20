from pecan import make_app

import logging

import sys



def setup_app(config):

    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)
    return app
