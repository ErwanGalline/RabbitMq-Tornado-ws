from tornado_websockets.websocket import WebSocket

'''
    Test application for WebSocket tests.
'''


def get_ws():
    ws = WebSocket('/test')

    @ws.on
    def hello(socket, data):
        ws.emit('hello', {
            'socket': str(socket),
            'data_sent': data,
            'message': 'Hello from hello callback!'
        })

    return ws
