from drillion.component import Component
from drillion.maths import Transform2

class TransformComponent(Component):
    def __init__(self, transform=Transform2()):
        super(TransformComponent, self).__init__()
        self.transform = Transform2(*transform)
