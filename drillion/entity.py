class Entity(object):
    def __init__(self, components=[]):
        self.components = list(components)
        self.game = None
        self.key = -1

    def create(self):
        for component in self.components:
            component.entity = self
            component.create()

    def delete(self):
        for component in reversed(self.components):
            component.delete()
            component.entity = None
