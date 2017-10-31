# coding: utf-8

"""
    Example of a « echo » websocket server by using `tornado_websocket.WebSocket`.
"""

from tornado_websockets.websocket import WebSocket

tws = WebSocket('/echo')


# Listen the « message » event
@tws.on
def message(socket, data):
    socket.emit('new_message', {
        'message': data.get('message')
    })

    # Shorter version
    # socket.emit('new_message', data)
