from cavear.entity import Entity
from cavear.maths import generate_circle_vertices, Transform
from cavear.sprite import PolygonSprite
from cavear.sprite_component import SpriteComponent

class BoulderEntityCreator(object):
    def create(self, position=(0.0, 0.0)):
        vertices = generate_circle_vertices(6)
        transform = Transform()
        transform.translate(*position)
        sprite = PolygonSprite(vertices, transform=transform)
        sprite_component = SpriteComponent(sprite)
        return Entity([sprite_component])
