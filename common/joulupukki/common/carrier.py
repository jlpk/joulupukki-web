import json

import pika

import pecan


import ast


from joulupukki.common.datamodel.build import Build
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.user import User
import logging


class Carrier(object):
    def __init__(self, server, port, exchange):
        """queues:
        * builds
        """
        self.server = server
        self.port = port
        self.exchange = exchange
        self.parameters = pika.ConnectionParameters(host=self.server,
                                                    port=self.port,
                                                    )
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def declare_builds(self):
        self.channel.queue_declare(queue='builds')

    def send_build(self, build):
        try:
            self.channel.basic_publish(exchange='',
                                       routing_key='builds',
                                       body=json.dumps(build.dumps())
                                      )
        except Exception as exp:
            # TODO
            logging.error(exp)
            print(exp)
            return False
        return True


    def get_build(self):
        try:
            method_frame, header_frame, body = self.channel.basic_get('builds')
            if body is None:
                return None
            build_data = json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
        except Exception as exp:
            # TODO
            print(exp)
            return None
        if build_data is not None:
            build = Build(build_data)
            build.user = User.fetch(build_data['username'], sub_objects=False)
            build.project = Project.fetch(build.user, build_data['project_name'], sub_objects=False)
            return build
        return None
