# coding=utf-8
from unittest import TestCase

import six
import tornado.web
from tornado.concurrent import Future
from tornado.escape import json_decode
from tornado.testing import gen_test

from tornado_websockets.modules import ProgressBar
from tornado_websockets.tests.helpers import WebSocketBaseTestCase
from tornado_websockets.tests.helpers import WebSocketHandlerForTests
from tornado_websockets.websocket import WebSocket

if six.PY2:
    from mock import patch, Mock, call
else:
    from unittest.mock import patch, Mock, call


class TestModuleProgressBar(TestCase):
    def test_construct_default_values(self):
        module_pb = ProgressBar()

        self.assertEqual(module_pb.name, 'module_progressbar')
        self.assertEqual(module_pb.min, 0)
        self.assertEqual(module_pb.max, 100)
        self.assertEqual(module_pb.current, module_pb.min)
        self.assertFalse(module_pb.indeterminate)

    def test_construct_min_gt_max(self):
        with self.assertRaisesRegexp(ValueError, '« min » .* not be greater or equal .* « max »'):
            ProgressBar(min=1, max=0)

    def test_construct_should_be_indeterminate(self):
        module_pb = ProgressBar(indeterminate=True)

        self.assertTrue(module_pb.indeterminate)

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_initialize(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar()
        module_pb.initialize = Mock()

        self.assertEqual(ws.modules, [])

        ws.bind(module_pb)

        self.assertEqual(ws.modules, [module_pb])
        module_pb.initialize.assert_called_with()

    def test_tick_and_is_done(self):
        module_pb = ProgressBar(min=0, max=3)
        module_pb.emit_update = Mock()
        module_pb.emit_done = Mock()

        self.assertEqual(module_pb.current, 0)
        self.assertFalse(module_pb.is_done())

        # 1st tick
        module_pb.tick()

        self.assertEqual(module_pb.current, 1)
        module_pb.emit_update.assert_called_with(None)
        self.assertFalse(module_pb.is_done())
        module_pb.emit_done.assert_not_called()

        # 2nd tick
        module_pb.tick('My label')

        self.assertEqual(module_pb.current, 2)
        module_pb.emit_update.assert_called_with('My label')
        self.assertFalse(module_pb.is_done())
        module_pb.emit_done.assert_not_called()

        # 3rd tick
        module_pb.tick('My other label')

        self.assertEqual(module_pb.current, 3)
        module_pb.emit_update.assert_called_with('My other label')
        self.assertTrue(module_pb.is_done())
        module_pb.emit_done.assert_called_with()

    def test_reset(self):
        module_pb = ProgressBar()
        module_pb.emit_update = Mock()
        module_pb.emit_done = Mock()

        self.assertEqual(module_pb.min, 0)
        self.assertEqual(module_pb.current, module_pb.min)

        module_pb.tick()
        self.assertEqual(module_pb.current, 1)

        module_pb.tick()
        self.assertEqual(module_pb.current, 2)

        module_pb.reset()
        self.assertEqual(module_pb.current, module_pb.min)

    def test_is_done(self):
        module_pb = ProgressBar(min=0, max=100)
        self.assertFalse(module_pb.is_done())

        module_pb = ProgressBar(indeterminate=False)
        self.assertFalse(module_pb.is_done())

        module_pb = ProgressBar(min=0, max=1)
        module_pb.emit_update = Mock()
        module_pb.emit_done = Mock()
        module_pb.tick()
        self.assertEqual(module_pb.current, 1)
        self.assertTrue(module_pb.is_done())

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit_init_determinate(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar()

        ws.bind(module_pb)
        ws.emit = Mock()

        module_pb.emit_init()

        call1 = call('module_progressbar_before_init', None)
        call2 = call('module_progressbar_init', {
            'indeterminate': False,
            'min': 0,
            'max': 100,
            'current': 0
        })
        call3 = call('module_progressbar_after_init', None)

        ws.emit.assert_has_calls([call1, call2, call3])

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit_init_indeterminate(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar(indeterminate=True)

        ws.bind(module_pb)
        ws.emit = Mock()

        module_pb.emit_init()

        call1 = call('module_progressbar_before_init', None)
        call2 = call('module_progressbar_init', {
            'indeterminate': True
        })
        call3 = call('module_progressbar_after_init', None)

        ws.emit.assert_has_calls([call1, call2, call3])

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit_update_determinate(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar()

        ws.bind(module_pb)
        ws.emit = Mock()

        # 1st try, without label
        module_pb.tick()

        call1 = call('module_progressbar_before_update', None)
        call2 = call('module_progressbar_update', {
            'current': 1
        })
        call3 = call('module_progressbar_after_update', None)

        ws.emit.assert_has_calls([call1, call2, call3])
        ws.emit.reset_mock()

        # 2nd and last try, with label
        module_pb.tick('My label')

        call1 = call('module_progressbar_before_update', None)
        call2 = call('module_progressbar_update', {
            'current': 2,
            'label': 'My label'
        })
        call3 = call('module_progressbar_after_update', None)

        ws.emit.assert_has_calls([call1, call2, call3])

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit_update_indeterminate(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar(indeterminate=True)

        ws.bind(module_pb)
        ws.emit = Mock()

        # 1st try, without label
        module_pb.tick()

        call1 = call('module_progressbar_before_update', None)
        call2 = call('module_progressbar_update', {})
        call3 = call('module_progressbar_after_update', None)

        ws.emit.assert_has_calls([call1, call2, call3])
        ws.emit.reset_mock()

        # 2nd and last try, with label
        module_pb.tick('My label')

        call1 = call('module_progressbar_before_update', None)
        call2 = call('module_progressbar_update', {
            'label': 'My label'
        })
        call3 = call('module_progressbar_after_update', None)

        ws.emit.assert_has_calls([call1, call2, call3])

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit_done(self, add_handler):
        ws = WebSocket('pb')
        module_pb = ProgressBar(min=0, max=2)

        ws.bind(module_pb)
        ws.emit = Mock()
        module_pb.emit_init = Mock()
        module_pb.emit_update = Mock()

        # 1st try
        module_pb.tick()
        self.assertEqual(module_pb.current, 1)
        ws.emit.assert_not_called()

        # 2nd and last try
        module_pb.tick()
        self.assertEqual(module_pb.current, 2)
        self.assertEqual(module_pb.current, module_pb.max)
        ws.emit.assert_called_with('module_progressbar_done', None)


class TestModuleProgressBarCommunication(WebSocketBaseTestCase):
    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def get_app(self, add_handler):
        self.ws = WebSocket('pb')
        self.close_future = Future()

        return tornado.web.Application([
            ('/ws/module/pb', WebSocketHandlerForTests, {'websocket': self.ws, 'close_future': self.close_future}),
        ])

    @gen_test
    def test_open_event(self):
        @self.ws.on
        def open():
            self.ws.emit('opened')

        module_pb = ProgressBar()
        module_pb.emit_init = Mock()
        self.ws.bind(module_pb)

        ws_connection = yield self.ws_connect('/ws/module/pb')

        # 1st: clasical websocket on open event
        response = yield ws_connection.read_message()
        response = json_decode(response)

        self.assertDictEqual(response, {
            'event': 'opened',
            'data': {}
        })

        # 2nd: ProgressBar module on open event
        module_pb.emit_init.assert_called_with()

        self.close(ws_connection)
