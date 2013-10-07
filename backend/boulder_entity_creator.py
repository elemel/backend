from backend.entity import Entity
from backend.maths import generate_circle_vertices, Transform
from backend.sprite import PolygonSprite
from backend.sprite_component import SpriteComponent

class BoulderEntityCreator(object):
    def create(self, position=(0.0, 0.0)):
        vertices = generate_circle_vertices(6)
        transform = Transform()
        transform.translate(*position)
        sprite = PolygonSprite(vertices, transform=transform)
        sprite_component = SpriteComponent(sprite)
        return Entity([sprite_component])
