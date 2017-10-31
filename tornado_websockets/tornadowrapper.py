# coding: utf-8
import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket


class TornadoWrapper(object):
    """
        Wrapper for Tornado application and server handling.

        It let you access to Tornado app, handlers and settings everywhere in your code (it's really
        useful when you run ``runtornado`` management command and WebSockets management).
    """

    app = None
    server = None
    handlers = []

    @classmethod
    def start_app(cls, handlers=None, settings=None):
        """
            Initialize the Tornado web application with given handlers and settings.

            :param handlers: Handlers (routes) for Tornado
            :param settings: Settings for Tornado
            :type handlers: list
            :type settings: dict
            :return: None
        """

        if not handlers:
            handlers = []

        if not settings:
            settings = {}

        # Not `handlers += cls.handlers` because the wildcard handler should be the last value in handlers
        # list. See http://www.tornadoweb.org/en/stable/_modules/tornado/web.html#Application.add_handlers
        handlers = cls.handlers + handlers

        cls.app = tornado.web.Application(handlers, **settings)

    @classmethod
    def listen(cls, tornado_port):
        """
            Start the Tornado HTTP server on given port.

            :param tornado_port: Port to listen
            :type tornado_port: int
            :return: None

            .. todo:: Add support for HTTPS server.
        """

        if not cls.app:
            raise TypeError('Tornado application was not instantiated, call TornadoWrapper.start_app method.')

        cls.server = tornado.httpserver.HTTPServer(cls.app)
        cls.server.listen(tornado_port)

    @classmethod
    def loop(cls):
        """
            Run Tornado main loop and display configuration about Tornado handlers and settings.

            :return: None
        """
        tornado.ioloop.IOLoop.instance().start()

    @classmethod
    def add_handler(cls, handler):
        """
            Add an handler to Tornado app if it's defined, otherwise it add this handler to the
            TornadoWrapper.tornado_handlers list.

            :param handler: An handler which conforms
            :type handler: list|tuple
        """

        if isinstance(handler, tuple):
            handler = [handler]

        if cls.app:
            cls.app.add_handlers('.*', handler)
        else:
            # ``cls.handler = handler + cls.handler`` and not ``cls.handler += handler``,
            # see `TornadoWrapper.start_app` source to know why.
            cls.handlers = handler + cls.handlers
