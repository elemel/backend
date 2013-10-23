class DrawPhase(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(self,  handler):
        self._handlers.remove(handler)

    def draw(self, alpha):
        for handler in self._handlers:
            handler.draw(alpha)
