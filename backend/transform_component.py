from backend.component import Component
from backend.maths import Transform

class TransformComponent(Component):
    def __init__(self):
        super(TransformComponent, self).__init__()
        self.transform = Transform()
