from bromine.entity import Entity
from bromine.maths import generate_circle_vertices, Transform2
from bromine.sprite import PolygonSprite
from bromine.sprite_component import SpriteComponent

class BoulderEntityCreator(object):
    def create(self, position=(0.0, 0.0)):
        vertices = generate_circle_vertices(6)
        transform = Transform2()
        transform.translate(*position)
        sprite = PolygonSprite(vertices, transform=transform)
        sprite_component = SpriteComponent(sprite)
        return Entity([sprite_component])
