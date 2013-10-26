class Entity(object):
    def __init__(self, components=[], parent=None):
        self.components = list(components)
        self.game = None
        self.key = -1
        self._parent = parent
        self._children = []

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return iter(self._children)

    def create(self):
        for component in self.components:
            component.entity = self
            component.create()
        if self._parent is not None:
            self._parent._children.append(self)

    def delete(self):
        if self._parent is not None:
            self._parent._children.remove(self)
        for component in reversed(self.components):
            component.delete()
            component.entity = None

    def find_component(self, cls):
        for component in self.components:
            if isinstance(component, cls):
                return component
        return None
