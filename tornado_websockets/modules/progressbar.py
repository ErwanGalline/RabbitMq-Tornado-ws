# coding=utf-8
from tornado_websockets.modules.module import Module


class ProgressBar(Module):
    """
        Initialize a new ProgressBar module instance.

        If ``min`` and ``max`` values are equal, this progress bar has its indeterminate state
        set to ``True``.

        :param min: Minimum value
        :param max: Maximum value
        :type min: int
        :type max: int
    """

    def __init__(self, name='', min=0, max=100, indeterminate=False):
        if name:
            name = '_' + name
        super(ProgressBar, self).__init__('progressbar' + name)

        if max < min:
            raise ValueError('Param « min » can not be greater or equal than param « max ».')

        self.min = self.current = min
        self.max = max
        self.indeterminate = indeterminate

    def initialize(self):
        @self.on
        def open():
            self.emit_init()

    def tick(self, label=None):
        """
            Increments progress bar's _current by ``1`` and emit ``update`` event. Can also emit ``done`` event if
            progression is done.

            Call :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.emit_update` method each time this
            method is called.
            Call :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.emit_done` method if progression is
            done.

            :param label: A label which can be displayed on the client screen
            :type label: str
        """

        if not self.indeterminate and self.current < self.max:
            self.current += 1

        self.emit_update(label)

        if self.is_done():
            self.emit_done()

    def reset(self):
        """
            Reset progress bar's progression to its minimum value.
        """
        self.current = self.min

    def is_done(self):
        """
            Return ``True`` if progress bar's progression is done, otherwise ``False``.

            Returns ``False`` if progress bar is indeterminate, returns ``True`` if progress bar is
            determinate and current value is equals to ``max`` value.
            Returns ``False`` by default.

            :rtype: bool
        """

        if self.indeterminate:
            return False

        if self.current is self.max:
            return True

        return False

    def emit_init(self):
        """
            Emit ``before_init``, ``init`` and ``after_init`` events to initialize a client-side progress bar.

            If progress bar is not indeterminate, ``min``, ``max`` and ``value`` values are sent with ``init`` event.
        """

        data = {'indeterminate': self.indeterminate}

        if not self.indeterminate:
            data.update({
                'min': int(self.min),
                'max': int(self.max),
                'current': int(self.current),
            })

        self.emit('before_init')
        self.emit('init', data)
        self.emit('after_init')

    def emit_update(self, label=None):
        """
            Emit ``before_update``, ``update`` and ``after_update`` events to update a client-side progress bar.

            :param label: A label which can be displayed on the client screen
            :type label: str
        """

        data = {}

        if not self.indeterminate:
            data.update({'current': self.current})

        if label:
            data.update({'label': label})

        self.emit('before_update')
        self.emit('update', data)
        self.emit('after_update')

    def emit_done(self):
        """
            Emit ``done`` event when progress bar's progression
            :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.is_done`.
        """

        self.emit('done')
