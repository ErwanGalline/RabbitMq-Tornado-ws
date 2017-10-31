# Thanks to Ben Darnell for his file which show us
# how to make Tornado runs fine with Django and other WSGI Handler.
# => https://github.com/bdarnell/django-tornado-demo/blob/master/testsite/tornado_main.py

import json

import django.core.handlers.wsgi
from django.apps import AppConfig
from django.conf import settings
from django.core.management import BaseCommand

from tornado_websockets.tornadowrapper import TornadoWrapper

if django.VERSION[1] > 5:
    django.setup()

DEFAULT_PORT = 8000


def get_port(options, configuration):
    port = options.get('port')
    port = port or configuration.get('port')
    port = port or DEFAULT_PORT

    return port


def run(tornado_handlers, tornado_settings, port):
    TornadoWrapper.start_app(tornado_handlers, tornado_settings)
    TornadoWrapper.listen(port)
    TornadoWrapper.loop()


class Command(BaseCommand, AppConfig):
    help = 'Run Tornado web server with Django and WebSockets support'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='?', help='Optional port number', type=int)

    def handle(self, *args, **options):
        try:
            configuration = settings.TORNADO
        except AttributeError as e:
            self.stderr.write('runtornado: Configuration => Not found: %s.' % e)
            return

        port = get_port(options, configuration)
        tornado_handlers = configuration.get('handlers', [])
        tornado_settings = configuration.get('settings', {})

        self.stdout.write('runtornado: Configuration => Found.')
        self.stdout.write('runtornado: Port => %d.' % port)
        self.stdout.write('runtornado: Handlers => Found %d initial handlers.' % len(tornado_handlers))
        self.stdout.write('runtornado: Settings => ' + json.dumps(tornado_settings))

        run(tornado_handlers, tornado_settings, port)
