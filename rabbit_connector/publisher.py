#!/usr/bin/env python
import pika
import sys

MQ_SERVER_ADDR = 'localhost'
MQ_SERVER_PORT = 5673
# EXCHANGE_NAME = 'my_channel_exchange'

class Publisher():

    def publish(EXCHANGE_NAME , message) :
        connection = pika.BlockingConnection(pika.ConnectionParameters(MQ_SERVER_ADDR, MQ_SERVER_PORT))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE_NAME,
                                 exchange_type='fanout')

        # message = ' '.join(sys.argv[1:]) or "info: Hello World 3!"
        mssg_body = message.get('username') + ": "+message.get('message')
        channel.basic_publish(exchange=EXCHANGE_NAME,
                                  routing_key='',
                              body=mssg_body)
        # print(" ::: [x] Sent to rabbit  %r" % message.message)
        connection.close()