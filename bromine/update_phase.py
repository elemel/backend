class UpdatePhase(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(handler):
        self._handlers.remove(handler)

    def update(self, dt):
        for handler in self._handlers:
            handler.update(dt)
