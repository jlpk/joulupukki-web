import json

import pika
from pika.exceptions import AMQPConnectionError

import time

from joulupukki.common.datamodel.build import Build
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.user import User
import logging


class Carrier(object):
    def __init__(self, server, port, exchange, queue="default.queue"):
        """queues:
        * builds
        """
        self.server = server
        self.port = port
        self.exchange = exchange
        self.closing = False
        self.parameters = pika.ConnectionParameters(host=self.server,
                                                    port=self.port,
                                                    )
        self.queue = queue
        self.connect()
        # self.connection = pika.BlockingConnection(self.parameters)
        # self.channel = self.connection.channel()

    def connect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def on_connection_closed(self):
        self.channel = None
        if not self.closing:
            print("Connection closed, reopening in 5 seconds: (%s) %s")
            time.sleep(5)
            self.connect()
            self.declare_queue(self.queue)
            self.declare_builds()

    def declare_builds(self):
        self.channel.queue_declare(queue='builds')

    def declare_queue(self, queue='default.queue'):
        self.channel.queue_declare(queue=queue)

    def send_message(self, message, queue='default.queue'):
        try:
            self.channel.basic_publish(exchange='', routing_key=queue,
                                       body=json.dumps(message))
        except AMQPConnectionError:
            self.on_connection_closed()
            self.channel.basic_publish(exchange='', routing_key=queue,
                                       body=json.dumps(message))
        except Exception as exp:
            logging.error(exp)
            return False
        return True

    def send_build(self, build):
        try:
            self.channel.basic_publish(exchange='', routing_key='builds.queue',
                                       body=json.dumps(build.dumps()))
        except AMQPConnectionError:
            self.on_connection_closed()
            self.channel.basic_publish(exchange='', routing_key='builds.queue',
                                       body=json.dumps(build.dumps()))
        except Exception as exp:
            logging.error(exp)
            return False
        return True

    def get_build(self):
        build_data = self.get_message('builds.queue')
        if build_data is not None:
            build = Build(build_data)
            build.user = User.fetch(build_data['username'], sub_objects=False)
            build.project = Project.fetch(build.user,
                                          build_data['project_name'],
                                          sub_objects=False)
            return build

    def get_message(self, queue):
        message_data = None
        try:
            method_frame, header_frame, body = (
                self.channel.basic_get(queue)
            )
            if body is None:
                return None
            message_data = json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
        except AMQPConnectionError:
            self.on_connection_closed()

            method_frame, header_frame, body = (
                self.channel.basic_get(queue)
            )
            if body is None:
                return None
            message_data = json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)

        except Exception as exp:
            logging.error(exp)
            return None

        return message_data
