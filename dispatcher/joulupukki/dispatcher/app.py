from pecan import make_app

import logging

from dispatcher.manager import Manager
import sys

import signal





def setup_app(config):

    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)


    manager = Manager(app)
    manager.start()


    def signal_handler(signal, frame):
        logging.debug('You pressed Ctrl+C!')
        manager.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    return app
