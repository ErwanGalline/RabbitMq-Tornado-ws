API
===

WebSocket
---------

.. automodule:: tornado_websockets.websocket

    .. autoclass:: WebSocket
    .. automethod:: WebSocket.on
    .. automethod:: WebSocket.emit

WebSocketHandler
----------------

.. automodule:: tornado_websockets.websockethandler

    .. autoclass:: WebSocketHandler
    .. automethod:: WebSocketHandler.initialize
    .. automethod:: WebSocketHandler.on_message
    .. automethod:: WebSocketHandler.on_close
    .. automethod:: WebSocketHandler.emit

TornadoWrapper
--------------

.. automodule:: tornado_websockets.tornadowrapper

    .. autoclass:: TornadoWrapper
    .. automethod:: TornadoWrapper.add_handler
    .. automethod:: TornadoWrapper.start_app
    .. automethod:: TornadoWrapper.loop
    .. automethod:: TornadoWrapper.listen
