from bromine.component import Component

class SpriteComponent(Component):
    def __init__(self, sprite, batch):
        super(SpriteComponent, self).__init__()
        self.sprite = sprite
        self.batch = batch

    def create(self):
        self.sprite.batch = self.batch

    def delete(self):
        self.sprite.batch = None

