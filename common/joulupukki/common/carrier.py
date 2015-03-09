import json

import pika

import pecan


import ast


from joulupukki.common.datamodel.build import Build
from joulupukki.common.datamodel.project import Project
from joulupukki.common.datamodel.user import User


class Carrier(object):
    def __init__(self, server, port, exchange):
        self.server = server
        self.port = port
        self.exchange = exchange
        self.parameters = pika.ConnectionParameters(host=self.server,
                                                    port=self.port,
                                                    )
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='builds')
        
    def send_build(self, build):
        # prepare serialisation

        try:
            self.channel.basic_publish(exchange='',
                                       routing_key='builds',
                                       body=json.dumps(build.dumps())
                                      )
        except Exception as exp:
            # TODO
            print exp
            return False
        return True


    def get_build(self):
        try:
            method_frame, header_frame, body = self.channel.basic_get('builds')
            if body is None:
                return None
            build = json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
        except Exception as exp:
            # TODO
            print exp
            return None
        if build is not None:
            build['user'] = User(**build['user'])
            build['project']['user'] = build['user']
            build['project'] = Project(**build['project'])
            build = Build(**build)
        return build


