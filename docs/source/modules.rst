Modules
=======

.. automodule:: tornado_websockets.modules

Module
------

.. autoclass:: Module


Progress bar
------------

The module « ProgressBar » facilitate the communication between the server-side and client-side of a progression bar.

**Server-side**:

- An easier communication with client-side ProgressBar module
- Handle *init*, *update* and *done* events,
- Update current progression value with :py:meth:`~.tick()` or :py:meth:`~.reset()`

**Client-side**:

- An easier communication with server-side ProgressBar module,
- Handle *init*, *update* and *done* events,
- Rendering a progression bar by using `HTML5` or `Bootstrap` rendering.

Server-side
^^^^^^^^^^^

Construction
............

.. autoclass:: ProgressBar

Methods
.......

.. automethod:: ProgressBar.reset
.. automethod:: ProgressBar.tick
.. automethod:: ProgressBar.is_done

Events
......

.. automethod:: ProgressBar.on
.. automethod:: ProgressBar.emit_init
.. automethod:: ProgressBar.emit_update
.. automethod:: ProgressBar.emit_done

Example
.......

.. code-block:: python

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
            yield gen.sleep(.1)  # like time.sleep(), but asynchronous with @gen.engine
            progressbar.tick(label="[%d/%d] Tâche %d terminée" % (progressbar.current + 1, progressbar.max, value))


Client-side
^^^^^^^^^^^

Read documentation about ProgressBar client-side module `here <https://docs.kocal.fr/django-tornado-websockets-client/0.2.0-beta/ModuleProgressBar.html>`_.
