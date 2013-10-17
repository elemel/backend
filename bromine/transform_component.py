from bromine.component import Component
from bromine.maths import Transform2

class TransformComponent(Component):
    def __init__(self, transform=Transform2()):
        super(TransformComponent, self).__init__()
        self.transform = Transform2(*transform)
