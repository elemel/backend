from caveat.component import Component

class CollisionComponent(Component):
    def __init__(self, shape, detector):
        self._shape = shape
        self._detector

    def create(self):
        self._detector.add_shape(self._shape)

    def delete(self):
        self._detector.add_shape(self._shape)
