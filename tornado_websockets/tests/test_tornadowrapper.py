from _socket import gaierror
from unittest import TestCase

import tornado
import tornado.httpserver
import tornado.web
from mock import patch
from tornado.websocket import WebSocketHandler

from tornado_websockets.tornadowrapper import TornadoWrapper


class TestTornadoWrapper(TestCase):
    """
        Tests for TornadoWrapper class.
    """

    def tearDown(self):
        TornadoWrapper.app = None
        TornadoWrapper.handlers = []

    '''
        Tests for TornadoWrapper.start_app()
    '''

    @patch('tornado.web.Application')
    def test_start_app_without_handlers_without_settings(self, stub):
        TornadoWrapper.start_app()

        stub.assert_called_with([])

    @patch('tornado.web.Application')
    def test_start_app_with_handlers_with_settings(self, stub):
        TornadoWrapper.start_app([], {'foo': 'bar', 'foo2': 'bar2'})

        stub.assert_called_with([], foo='bar', foo2='bar2')

    '''
        Tests for TornadoWrapper.listen()
    '''

    def test_listen_with_bad_port_type(self):
        TornadoWrapper.start_app()

        with self.assertRaisesRegexp(gaierror, 'Servname not supported'):
            TornadoWrapper.listen('not a integer')

    def test_listen_without_app_instance(self):
        with self.assertRaisesRegexp(TypeError, 'Tornado application was not instantiated'):
            TornadoWrapper.listen(8000)

    @patch('tornado.httpserver.HTTPServer', autospec=True)
    def test_listen_with_app_instance(self, stub):
        self.assertIsNone(TornadoWrapper.app)
        self.assertIsNone(TornadoWrapper.server)

        TornadoWrapper.start_app()
        TornadoWrapper.listen(12345)

        self.assertIsInstance(TornadoWrapper.app, tornado.web.Application)
        self.assertIs(stub, tornado.httpserver.HTTPServer)
        stub.assert_called_with(TornadoWrapper.app)

    '''
        Test for TornadoWrapper.loop()
    '''

    @patch('tornado.ioloop.IOLoop.instance')
    def test_loop(self, stub):
        TornadoWrapper.loop()

        stub.assert_called()

    '''
        Tests for TornadoWrapper.add_handler()
    '''

    def test_add_handler_without_tornado_app_instance(self):
        self.assertIsNone(TornadoWrapper.app)
        self.assertListEqual(TornadoWrapper.handlers, [])

        with self.assertRaises(TypeError):
            TornadoWrapper.add_handler('a string')

        self.assertListEqual(TornadoWrapper.handlers, [])

        TornadoWrapper.add_handler([('my', 'tuple', 'in', 'a', 'list')])
        self.assertListEqual(TornadoWrapper.handlers, [('my', 'tuple', 'in', 'a', 'list')])

        TornadoWrapper.add_handler(('my', 'tuple'))
        self.assertListEqual(TornadoWrapper.handlers, [('my', 'tuple'), ('my', 'tuple', 'in', 'a', 'list')])

    def test_add_handler_with_tornado_app_instance(self):
        self.assertIsNone(TornadoWrapper.app)
        self.assertListEqual(TornadoWrapper.handlers, [])

        TornadoWrapper.start_app()
        self.assertIsNotNone(TornadoWrapper.app)

        with self.assertRaisesRegexp(AttributeError, "'str' object has no attribute 'name'"):
            TornadoWrapper.add_handler('a string')

        TornadoWrapper.add_handler([('path', WebSocketHandler, {})])
        TornadoWrapper.add_handler(('path2', WebSocketHandler, {}))
