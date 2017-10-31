# coding: utf-8

"""
    Example of a « chat application » by using `tornado_websocket.WebSocket` to handle communications,
    and Django's TemplateView for rendering.
"""

from django.views.generic import TemplateView

from tornado_websockets.websocket import WebSocket
import rabbit_connector.consumer as rabbit_consumer
from  rabbit_connector.publisher import Publisher
import threading

EXCHANGE_NAME = 'my_channel_exchange'
tws = WebSocket('/my_chat')


class MyChat(TemplateView):
    """
        Proof of concept about a really simple web chat using websockets and supporting messages history
    """

    template_name = 'testapp/index.html'

    def __init__(self):
        self.messages = []

    def __init__(self, **kwargs):
        super(MyChat, self).__init__(**kwargs)

        # Otherwise, 'self' parameter for method decorated by @ws_chat.on will not be defined
        tws.context = self

    def send_to_rabbit(message , topic):
        print(":::send to rabbit ...")

        Publisher.publish(topic,message)

    def add_rabbit_client(self, topic):
        new_consumer = rabbit_consumer.Consumer(EXCHANGE_NAME, MyChat.rabbit_callback)
        tread = threading.Thread(target=new_consumer.start_consuming)
        tread.start()
        tread.join(0)
        print(":::New pika client init ...")

    def rabbit_callback(message_body):
        # message = {
        #     'username': data.get('username', '<Anonymous>'),
        #     'message': data.get('message', 'Empty message')
        # }
        print(":::Rabbit callback ...")
        # to_send.data = message_body

        to_send = message_body
        tws.emit('new_message', to_send )

    @tws.on
    def connection(self, socket, data):
        # Send an history of the chat
        # [socket.emit('new_message', __) for __ in self.messages]
        MyChat.add_rabbit_client(data, EXCHANGE_NAME)
        #tws.emit('new_connection', '%s just joined the webchat.' % data.get('username', '<Anonymous>'))

    @tws.on
    def message(self, socket, data):
        message = {
            'username': data.get('username', '<Anonymous>'),
            'message': data.get('message', 'Empty message')
        }

        MyChat.send_to_rabbit(message, EXCHANGE_NAME)
        # tws.emit('new_message', message)
        # self.messages.append(message)

    @tws.on
    def clear_history(self, socket, data):
        """
            Called when a client wants to clear messages history.
            Used only for client-side JavaScript unit tests
        """
        self.messages = []

    @tws.on
    def close(self, socket):
        message = {
            'username': 'username',
            'message': 'close'
        }
        tws.emit('new_message', message)
