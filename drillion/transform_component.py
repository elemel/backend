from drillion.component import Component
from drillion.maths import Transform2

class TransformComponent(Component):
    def __init__(self, transform=Transform2(), parent=None):
        super(TransformComponent, self).__init__()
        self._transform = Transform2(*transform)
        self._parent = parent
        self._children = []

    def create(self):
        if self._parent is not None:
            self._parent._children.append(self)

    def delete(self):
        while self._children:
            child = self._children.pop()
            child._parent = None
        if self._parent is not None:
            self._parent._children.remove(self)

    @property
    def transform(self):
        return self._transform

    @property
    def world_transform(self):
        transform = Transform2(*self._transform)
        component = self._parent
        while component is not None:
            transform.right_multiply(*component._transform)
            component = component._parent
        return transform
