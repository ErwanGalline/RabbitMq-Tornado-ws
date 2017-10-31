#!/usr/bin/env python
import pika

MQ_SERVER_ADDR = 'localhost'
MQ_SERVER_PORT = 5673
# EXCHANGE_NAME = 'my_channel_exchange'


class Consumer(object):

    def __init__(self , ex_name , callback):
        connection = pika.BlockingConnection(pika.ConnectionParameters(MQ_SERVER_ADDR, MQ_SERVER_PORT))
        self.channel = connection.channel()
        self.ws_callback = callback
        self.channel.exchange_declare(exchange=ex_name,
                                      exchange_type='fanout')

        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=ex_name,
                                queue=queue_name)

        print(' [*] Waiting for logs. To exit press CTRL+C')

        self.channel.basic_consume(self.callback,
                                   queue=queue_name,
                                   no_ack=True)
        # self.start_consuming()

    def callback(self, ch, method, properties, body):
        self.ws_callback(str(body))

    def start_consuming(self):
        self.channel.start_consuming()
