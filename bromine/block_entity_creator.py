from bromine.collision import CollisionBody
from bromine.collision_component import CollisionComponent
from bromine.color_generator import ColorGenerator, ClampedGaussGenerator
from bromine.entity import Entity
from bromine.maths import cf2ub, generate_circle_vertices, Polygon2, Transform2
from bromine.sprite import PolygonSprite
from bromine.sprite_component import SpriteComponent
from bromine.transform_component import TransformComponent

import random

class BlockEntityCreator(object):
    def __init__(self, collision_detector, batch):
        self._collision_detector = collision_detector
        self._batch = batch

        hue = random.uniform(0.0, 1.0)
        self._color_generator = ColorGenerator(
            hue_generator=ClampedGaussGenerator(hue, 0.05),
            lightness_generator=ClampedGaussGenerator(0.4, 0.1),
            saturation_generator=ClampedGaussGenerator(0.2, 0.05),
        )

    def create(self, grid_position):
        grid_x, grid_y = grid_position
        x1 = 2.0 * float(grid_x)
        y1 = 2.0 * float(grid_y)
        x2 = 2.0 * float(grid_x + 1)
        y2 = 2.0 * float(grid_y + 1)
        vertices = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        polygon = Polygon2(vertices)

        transform = Transform2()
        transform_component = TransformComponent(transform)

        collision_body = CollisionBody(polygon, transform)
        collision_component = CollisionComponent(transform_component, None,
                                                 collision_body,
                                                 self._collision_detector)

        float_color = self._color_generator.generate()
        color = tuple(cf2ub(c) for c in float_color)
        sprite = PolygonSprite(vertices, color=color, transform=transform)
        sprite_component = SpriteComponent(sprite, self._batch)

        components = [transform_component, collision_component,
                      sprite_component]
        entity = Entity(components)
        collision_body.user_data = 'block', entity
        return entity
