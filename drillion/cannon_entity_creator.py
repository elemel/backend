from drillion.animation_component import AnimationComponent
from drillion.collision import CollisionBody
from drillion.collision_component import CollisionComponent
from drillion.entity import Entity
from drillion.maths import Polygon2, Transform2
from drillion.sprite import PolygonSprite
from drillion.sprite_component import SpriteComponent
from drillion.transform_component import TransformComponent

import random

class CannonEntityCreator(object):
    def __init__(self, animation_update_phase, draw_phase, batch):
        self._animation_update_phase = animation_update_phase
        self._draw_phase = draw_phase
        self._batch = batch

    def create(self, ship_entity, position=(0.0, 0.0), angle=0.0, length=1.0,
               width=0.1, color=(255, 255, 255, 255)):
        vertices = [(0.0, -0.5), (1.0, -0.5), (1.0, 0.5), (0.0, 0.5)]
        polygon = Polygon2(vertices)

        parent_transform_component = \
            ship_entity.find_component(TransformComponent)

        transform = Transform2()
        transform.rotate(angle)
        transform.scale(length, width)
        transform.translate(*position)
        transform_component = \
            TransformComponent(transform, parent=parent_transform_component)

        sprite = PolygonSprite(vertices, color=color, transform=transform)
        sprite_component = SpriteComponent(sprite, self._batch)
        animation_component = AnimationComponent(transform_component,
                                                 sprite_component,
                                                 self._animation_update_phase,
                                                 self._draw_phase)

        components = [transform_component, sprite_component,
                      animation_component]
        return Entity(components, parent=ship_entity)
