import time

class UpdatePhase(object):
    def __init__(self, name):
        self._name = name
        self._handlers = []
        self._total_time = 0.0

    @property
    def name(self):
        return self._name

    @property
    def total_time(self):
        return self._total_time

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(self, handler):
        self._handlers.remove(handler)

    def update(self, dt):
        start_time = time.clock()
        for handler in self._handlers:
            handler.update(dt)
        end_time = time.clock()
        self._total_time += end_time - start_time
