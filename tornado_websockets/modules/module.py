import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Module(object):
    @abc.abstractmethod
    def __init__(self, name=''):
        self.name = 'module_' + name
        self._websocket = None  # will be initialized with WebSocket.bind(Module)

    @abc.abstractmethod
    def initialize(self):
        pass

    @property
    def context(self):
        return self._websocket.context

    @context.setter
    def context(self, value):
        self._websocket.context = value

    def on(self, callback):
        """
            Shortcut for :meth:`tornado_websockets.websocket.WebSocket.on` decorator,
            but with a specific prefix for each module.

            :param callback: function or a class method.
            :type callback: Callable
            :return: ``callback`` parameter.
        """

        callback.__name__ = self.name + '_' + callback.__name__

        return self._websocket.on(callback)

    def emit(self, event, data=None):
        """
            Shortcut for :meth:`tornado_websockets.websocket.WebSocket.emit` method,
            but with a specific prefix for each module.
        """

        return self._websocket.emit(self.name + '_' + event, data)
