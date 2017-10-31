# coding: utf-8

from unittest import TestCase

import six

from tornado_websockets.exceptions import NotCallableError
from tornado_websockets.modules import ProgressBar
from tornado_websockets.websocket import WebSocket
from tornado_websockets.websockethandler import WebSocketHandler

if six.PY2:
    from mock import patch, Mock
else:
    from unittest.mock import patch, Mock


class TestWebSocket(TestCase):
    """
        Tests for the class « WebSocket ».
    """

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_construct(self, add_handler):
        add_handler.assert_called_with(('/ws/path1', WebSocketHandler, {'websocket': WebSocket('path1')}))
        add_handler.assert_called_with(('/ws/path2', WebSocketHandler, {'websocket': WebSocket('/path2')}))
        add_handler.assert_called_with(('/ws/path3', WebSocketHandler, {'websocket': WebSocket('  path3  ')}))
        add_handler.assert_called_with(('/ws/path4', WebSocketHandler, {'websocket': WebSocket('   /path4 ')}))

        with self.assertRaisesRegexp(TypeError, '« Path » parameter should be a string.'):
            WebSocket(path=1234)

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_bind_module(self, add_handler):
        ws = WebSocket('path')
        module = ProgressBar('progress')

        module.initialize = Mock()

        self.assertListEqual(ws.modules, [])
        self.assertIsNone(module._websocket)
        module.initialize.assert_not_called()

        ws.bind(module)

        self.assertListEqual(ws.modules, [module])
        self.assertEqual(module._websocket, ws)
        module.initialize.assert_called_with()

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_on(self, add_handler):
        ws = WebSocket('path')

        self.assertDictEqual(ws.events, {})

        with self.assertRaises(NotCallableError):
            ws.on('string')

        @ws.on
        def func():
            pass

        self.assertDictEqual(ws.events, {'func': func})

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit(self, add_handler):
        ws = WebSocket('path')
        handler = Mock()

        # Emulate WebSocketHandler class with Mock, because only Tornado can instantiate it properly
        def side_effect(websocket):
            ws.handlers.append(handler)
            handler.websocket = websocket

        handler.return_value = None
        handler.websocket = None
        handler.initialize.side_effect = side_effect
        handler.emit = Mock()

        self.assertListEqual(ws.handlers, [])
        self.assertIsNone(handler.websocket)

        handler.initialize(ws)

        self.assertListEqual(ws.handlers, [handler])
        self.assertEqual(handler.websocket, ws)

        with self.assertRaisesRegexp(TypeError, 'Param « event » should be a string.'):
            ws.emit(123)
        handler.emit.assert_not_called()

        ws.emit('event')
        handler.emit.assert_called_with('event', {})
        handler.emit.reset_mock()

        ws.emit('event', {})
        handler.emit.assert_called_with('event', {})
        handler.emit.reset_mock()

        ws.emit('event', 'my message')
        handler.emit.assert_called_with('event', {'message': 'my message'})
        handler.emit.reset_mock()

        with self.assertRaisesRegexp(TypeError, 'Param « data » should be a string or a dictionary.'):
            ws.emit('event', 123)
        handler.emit.assert_not_called()
