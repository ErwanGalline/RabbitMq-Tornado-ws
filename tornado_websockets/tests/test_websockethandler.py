import unittest

import tornado.httpclient
import tornado.web
from mock import patch, ANY
from tornado.concurrent import Future
from tornado.escape import json_decode, json_encode
from tornado.testing import gen_test

from tornado_websockets.tests.app import ws as appTest
from tornado_websockets.tests.helpers import WebSocketBaseTestCase, WebSocketHandlerForTests
from tornado_websockets.websockethandler import WebSocketHandler


class WebSocketHandlerTest(WebSocketBaseTestCase):
    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def get_app(self, add_handler):
        self.ws = appTest.get_ws()
        self.close_future = Future()

        return tornado.web.Application([
            ('/ws/test', WebSocketHandlerForTests, {'websocket': self.ws, 'close_future': self.close_future}),
        ])

    @gen_test
    def test_connection_on_existing_websocket(self):
        ws_connection = yield self.ws_connect('/ws/test')

        self.assertEqual(None, ws_connection.close_code)
        self.assertEqual(None, ws_connection.close_reason)

        self.close(ws_connection)

    @gen_test
    def test_connection_on_non_existing_websocket(self):
        with self.assertRaisesRegexp(tornado.httpclient.HTTPError, 'HTTP 404: Not Found'):
            yield self.ws_connect('/ws/foo/bar')

    @gen_test
    def test_initialize(self):
        self.assertListEqual(self.ws.handlers, [])

        ws_connection = yield self.ws_connect('/ws/test')

        self.assertIsInstance(self.ws.handlers[0], WebSocketHandlerForTests)
        self.assertIsInstance(self.ws.handlers[0], WebSocketHandler)
        self.assertEqual(self.ws.handlers[0].websocket, self.ws)

        self.close(ws_connection)

    @unittest.expectedFailure
    @gen_test
    def test_open_without_open_event(self):
        @self.ws.on
        def open():
            self.ws.emit('opened')

        self.assertDictEqual(self.ws.events, {
            'hello': ANY
        })

        ws_connection = yield self.ws_connect('/ws/test')

        # Waiting for nonexistent open event
        yield ws_connection.read_message()

    @gen_test
    def test_open_event_with_open(self):
        @self.ws.on
        def open():
            self.ws.emit('opened')

        self.assertDictEqual(self.ws.events, {
            'hello': ANY,
            'open': open
        })

        ws_connection = yield self.ws_connect('/ws/test')

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'opened',
            'data': {}
        })

        self.close(ws_connection)

    @gen_test
    def test_on_message(self):
        ws_connection = yield self.ws_connect('/ws/test')

        # Test for invalid JSON
        ws_connection.write_message('Not a JSON')

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'warning',
            'data': {
                'message': 'Invalid JSON was sent.'
            }
        })

        # Test when there is no event
        ws_connection.write_message(json_encode({
            'data': {'message': 'my message'}
        }))

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'warning',
            'data': {
                'message': 'There is no event in this JSON.'
            }
        })

        # Test when the data is not a dict
        self.assertDictEqual(self.ws.events, {'hello': ANY})

        ws_connection.write_message(json_encode({
            'event': 'hello',
            'data': 'not a dict'
        }))

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'warning',
            'data': {
                'message': 'The data should be a dictionary.'
            }
        })

        # Test for socket and data params
        self.assertDictEqual(self.ws.events, {'hello': ANY})

        ws_connection.write_message(json_encode({
            'event': 'hello',
            'data': {
                'foo': 'FOO',
                'bar': 'BAR'
            }
        }))

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'hello',
            'data': {
                'socket': str(self.ws.handlers[0]),
                'message': 'Hello from hello callback!',
                'data_sent': {
                    'foo': 'FOO',
                    'bar': 'BAR'
                }
            }
        })

    @gen_test
    def test_on_message_without_context(self):
        ws = self.ws
        ws_connection = yield self.ws_connect('/ws/test')

        class WithoutContext(object):
            @ws.on
            def without_context(self, socket, data):
                assert self is None
                ws.emit('without_context', 'fail')

        WithoutContext()

        self.assertDictEqual(ws.events, {
            'hello': ANY,
            'without_context': ANY
        })

        ws_connection.write_message(json_encode({'event': 'without_context'}))
        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'without_context',
            'data': {
                'message': 'fail'
            }
        })

        self.close(ws_connection)

    @gen_test
    def test_on_message_with_context(self):
        ws = self.ws
        ws_connection = yield self.ws_connect('/ws/test')

        class WithContext(object):
            def __init__(self):
                ws.context = self

            @ws.on
            def with_context(self, socket, data):
                assert self is not None
                ws.emit('with_context', 'ok')

        WithContext()

        self.assertDictEqual(self.ws.events, {
            'hello': ANY,
            'with_context': ANY
        })

        ws_connection.write_message(json_encode({'event': 'with_context'}))

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'with_context',
            'data': {
                'message': 'ok'
            }
        })

        self.close(ws_connection)

    @unittest.expectedFailure
    @gen_test(timeout=1)
    def test_on_message_when_nonexistent_event(self):
        ws_connection = yield self.ws_connect('/ws/test')

        # Test when the event is not binded
        self.assertDictEqual(self.ws.events, {'hello': ANY})

        ws_connection.write_message(json_encode({
            'event': 'bye',
            'data': {'message': 'Bye !'}
        }))

        # Throw TimeoutError and/or StopIteration, because WebSocketHandler.on_message() does not send
        # any message when the client send a nonexistent event ('bye' in our case).
        # Also, I don't know how catch them, because self.assertRaises() and try/catch don't work.
        # So I use @unittest.expectedFailure here, but it's a bit dirty imo.
        yield ws_connection.read_message()

    @gen_test
    def test_emit(self):
        ws_connection = yield self.ws_connect('/ws/test')

        self.assertEqual(self.ws.events, {'hello': ANY})
        self.assertNotEqual(self.ws.handlers, [])
        self.ws.handlers[0].emit('my_event', {'my': 'data'})

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'my_event',
            'data': {
                'my': 'data'
            }
        })

        self.close(ws_connection)

    @gen_test
    def test_emit_warning(self):
        ws_connection = yield self.ws_connect('/ws/test')

        self.assertEqual(self.ws.events, {'hello': ANY})
        self.assertNotEqual(self.ws.handlers, [])
        self.ws.handlers[0].emit_warning('WARNING!')

        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'warning',
            'data': {
                'message': 'WARNING!'
            }
        })

        self.close(ws_connection)

    @gen_test
    def test_on_close(self):
        self.assertEqual(self.ws.handlers, [])

        ws_connection = yield self.ws_connect('/ws/test')
        self.assertNotEqual(self.ws.handlers, [])

        self.close(ws_connection)
        yield self.close_future

        self.assertEqual(self.ws.handlers, [])
