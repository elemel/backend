from drillion.animation_component import AnimationComponent
from drillion.collision import CollisionBody
from drillion.collision_component import CollisionComponent
from drillion.entity import Entity
from drillion.maths import Polygon2
from drillion.physics_component import PhysicsComponent
from drillion.sprite import PolygonSprite
from drillion.sprite_component import SpriteComponent
from drillion.transform_component import TransformComponent

class BulletEntityCreator(object):
    def __init__(self, physics_update_phase, collision_transform_update_phase,
                 animation_update_phase, draw_phase, collision_detector,
                 batch):
        self._physics_update_phase = physics_update_phase
        self._collision_transform_update_phase = \
            collision_transform_update_phase
        self._animation_update_phase = animation_update_phase
        self._draw_phase = draw_phase
        self._collision_detector = collision_detector
        self._batch = batch

    def create(self, position=(0.0, 0.0), velocity=(0.0, 0.0),
               color=(255, 255, 255, 255)):
        transform_component = TransformComponent()

        physics_component = PhysicsComponent(transform_component,
                                             self._physics_update_phase,
                                             position=position,
                                             velocity=velocity)

        collision_vertices = [(0.0, 0.0)]
        collision_polygon = Polygon2(collision_vertices)
        collision_body = CollisionBody(collision_polygon, seed=True)
        collision_component = \
            CollisionComponent(transform_component,
                               self._collision_transform_update_phase,
                               collision_body, self._collision_detector)

        sprite_radius = 0.1
        sprite_vertices = [
            (-sprite_radius, -sprite_radius),
            (sprite_radius, -sprite_radius),
            (sprite_radius, sprite_radius),
            (-sprite_radius, sprite_radius),
        ]
        sprite = PolygonSprite(sprite_vertices, color=color)
        sprite_component = SpriteComponent(sprite, self._batch)

        animation_component = AnimationComponent(transform_component,
                                                 sprite_component,
                                                 self._animation_update_phase,
                                                 self._draw_phase)

        components = [transform_component, physics_component,
                      collision_component, sprite_component,
                      animation_component]
        entity = Entity(components)
        collision_body.user_data = 'bullet', entity
        return entity
