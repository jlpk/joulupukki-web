from pecan import make_app

import logging

from worker.manager import Manager
import sys

import signal


def setup_app(config):

    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)

    thread_count = config.thread_count
    threads = []
    for i in range(thread_count):
        th = Manager(app)
        th.start()
        threads.append(th)

    def signal_handler(signal, frame):
        logging.debug('You pressed Ctrl+C!')
        for th in threads:
            th.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    return app
