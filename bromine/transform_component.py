from bromine.component import Component
from bromine.maths import Transform

class TransformComponent(Component):
    def __init__(self):
        super(TransformComponent, self).__init__()
        self.transform = Transform()
