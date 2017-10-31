from tornado_websockets.websockethandler import WebSocketHandler


class WebSocketHandlerForTests(WebSocketHandler):
    """Base class for testing handlers that exposes the on_close event.
    This allows for deterministic cleanup of the associated socket.
    """

    def initialize(self, websocket, close_future, compression_options=None):
        super(WebSocketHandlerForTests, self).initialize(websocket)
        self.close_future = close_future
        self.compression_options = compression_options

    def get_compression_options(self):
        return self.compression_options

    def on_close(self):
        super(WebSocketHandlerForTests, self).on_close()
        self.close_future.set_result((self.close_code, self.close_reason))
