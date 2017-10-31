# coding: utf-8

"""
    Example of module « Progress Bar » by using `tornado_websocket.modules.ProgressBar` to handle communications,
    and Django's TemplateView for rendering.
"""

from django.views.generic import TemplateView
from tornado import gen

from tornado_websockets.modules import ProgressBar
from tornado_websockets.websocket import WebSocket

ws = WebSocket('module_progressbar')
progressbar = ProgressBar('foo', min=0, max=100)

ws.bind(progressbar)


@progressbar.on
def reset():
    progressbar.reset()


@progressbar.on
@gen.engine  # Make this function asynchronous for Tornado's IOLoop
def start():
    for value in range(0, progressbar.max):
        yield gen.sleep(.1)  # like time.sleep(), but asynchronous
        progressbar.tick(label="[%d/%d] Tâche %d terminée" % (progress_bar.current + 1, progress_bar.max, value))


class MyProgressBar(TemplateView):
    template_name = 'testapp/progress_bar.html'
