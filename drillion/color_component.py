from drillion.component import Component

class ColorComponent(Component):
    def __init__(self, color=(255, 255, 255, 255)):
        super(ColorComponent, self).__init__()
        self.color = tuple(color)
