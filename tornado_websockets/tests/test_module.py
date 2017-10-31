from unittest import TestCase

import six

from tornado_websockets.tests.modules import Module1, Module2, Module3
from tornado_websockets.tests.modules import MyModule
from tornado_websockets.websocket import WebSocket

if six.PY2:
    from mock import patch, Mock
else:
    from unittest.mock import patch, Mock


class TestModule(TestCase):
    def test_abstraction(self):
        # Module1.__init__() and Module1.initialize() are abstract
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class Module1"):
            Module1()

        # Module2.initialize() is abstract
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class Module2.* initialize"):
            Module2()

        # Module3 is ok!
        Module3()

    def test_construct(self):
        moduleFoo = MyModule()
        moduleBar = MyModule('bar')

        self.assertEqual(moduleFoo.name, 'module_mymodule')
        self.assertEqual(moduleBar.name, 'module_mymodule_bar')

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_context(self, add_handler):
        module = MyModule()
        ws = WebSocket('pb')

        self.assertIsNone(module._websocket)
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'context'"):
            print(module.context)

        ws.bind(module)

        module.context = 'foo'
        self.assertEqual(module._websocket.context, 'foo')
        self.assertEqual(module.context, 'foo')

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_on(self, add_handler):
        ws = WebSocket('foo')
        moduleBar = MyModule('bar')
        moduleBar.initialize = Mock()

        # Module is not binded to WebSocket instance
        self.assertEqual(ws.modules, [])
        self.assertEqual(ws.events, {})
        self.assertIsNone(moduleBar._websocket)
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'on'"):
            @moduleBar.on
            def func_a():
                pass

        # Module is now binded to WebSocket instance
        ws.bind(moduleBar)
        moduleBar.initialize.assert_called_with()

        self.assertEqual(ws.modules, [moduleBar])
        self.assertEqual(ws.events, {})
        self.assertEqual(moduleBar._websocket, ws)

        @moduleBar.on
        def func_b():
            pass

        self.assertDictEqual(ws.events, {'module_mymodule_bar_func_b': func_b})

    @patch('tornado_websockets.tornadowrapper.TornadoWrapper.add_handler')
    def test_emit(self, add_handler):
        ws = WebSocket('foo')
        ws.emit = Mock()
        moduleBar = MyModule('bar')
        moduleBar.initialize = Mock()

        # Module is not binded to WebSocket instance
        self.assertEqual(ws.modules, [])
        self.assertEqual(ws.events, {})
        self.assertIsNone(moduleBar._websocket)
        with self.assertRaisesRegexp(AttributeError, "'NoneType' object has no attribute 'emit'"):
            moduleBar.emit('my_event', {'my': 'data'})
        ws.emit.assert_not_called()

        # Module is now binded to WebSocket instance
        ws.bind(moduleBar)

        moduleBar.initialize.assert_called_with()

        self.assertEqual(ws.modules, [moduleBar])
        self.assertEqual(ws.events, {})
        self.assertEqual(moduleBar._websocket, ws)

        moduleBar.emit('my_event', {'my': 'data'})

        ws.emit.assert_called_with('module_mymodule_bar_my_event', {'my': 'data'})
