from pecan import make_app
from joulupukki.web import model

import logging

from worker.logger import Logger
import sys

import signal





def setup_app(config):

    model.init_model()
    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)


    logger = Logger()
    logger.start()


    def signal_handler(signal, frame):
        logging.debug('You pressed Ctrl+C!')
        logger.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    return app
