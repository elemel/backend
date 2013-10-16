from cavear.component import Component

class SpriteComponent(Component):
    def __init__(self, sprite):
        super(SpriteComponent, self).__init__()
        self.sprite = sprite

    def create(self):
        self.sprite.batch = self.entity.game.batch

    def delete(self):
        self.sprite.batch = None

