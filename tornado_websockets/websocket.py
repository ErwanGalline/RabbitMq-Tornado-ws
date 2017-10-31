# coding: utf-8

from six import string_types

from .exceptions import NotCallableError
from .tornadowrapper import TornadoWrapper
from .websockethandler import WebSocketHandler


class WebSocket(object):
    """
        Class that you should to make WebSocket applications 👍.
    """

    def __init__(self, path):
        """
            Initialize a new WebSocket object.

            :param path: path of your application, used to rely with dtws's client side.
            :type path: str
        """

        self.events = {}
        self.handlers = []
        self.context = None
        self.modules = []

        if not isinstance(path, string_types):
            raise TypeError('« Path » parameter should be a string.')

        self.path = path.strip()
        self.path = self.path if self.path.startswith('/') else '/' + self.path

        TornadoWrapper.add_handler(('/ws' + self.path, WebSocketHandler, {'websocket': self}))

    def bind(self, module):
        """
            Bind a Module instance to a WebSocket one.

            :param module: Module instance to bind
            :type module: tornado_websockets.modules.Module
        """

        self.modules.append(module)
        module._websocket = self
        module.initialize()

    def on(self, callback):
        """
            Should be used as a decorator.

            It will execute the decorated function when :class:`~tornado_websockets.websockethandler.WebSocketHandler`
            will receive an event where its name correspond to the function (by using ``__name__`` magic attribute).

            :param callback: Function to decorate.
            :type callback: callable
            :raise tornado_websockets.exceptions.NotCallableError:

            :Example:
                 >>> ws = WebSocket('/example')
                 >>> @ws.on
                 ... def hello(socket, data):
                 ...     print('Received event « hello » from a client.')
        """

        if not callable(callback):
            raise NotCallableError(callback)

        self.events[callback.__name__] = callback
        return callback

    def emit(self, event, data=None):
        """
            Send an event/data dictionnary to all clients connected to your WebSocket instance.
            To see all ways to emit an event, please read « :ref:`emit-an-event` » section.

            :param event: event name
            :param data: a dictionary or a string which will be converted to ``{'message': data}``
            :type event: str
            :type data: dict or str
            :raise: :class:`~tornado_websockets.exceptions.EmitHandlerError` if not used inside
                    :meth:`@WebSocket.on() <tornado_websockets.websocket.WebSocket.on>` decorator.
            :raise: :class:`tornado.websocket.WebSocketClosedError` if connection is closed.

            .. warning::
                :meth:`WebSocket.emit() <tornado_websockets.websocket.WebSocket.emit>` method should be used inside
                a function or a class method decorated by :meth:`@WebSocket.on()
                <tornado_websockets.websocket.WebSocket.on>` decorator, otherwise it will raise a
                :class:`~tornado_websockets.exceptions.EmitHandlerError` exception.
        """

        if not isinstance(event, string_types):
            raise TypeError('Param « event » should be a string.')

        if not data:
            data = {}

        if isinstance(data, string_types):
            data = {'message': data}

        if not isinstance(data, dict):
            raise TypeError('Param « data » should be a string or a dictionary.')

        if self.handlers:
            for handler in self.handlers:
                handler.emit(event, data)
