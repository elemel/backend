from drillion.animation_component import AnimationComponent
from drillion.collision import CollisionBody
from drillion.collision_component import CollisionComponent
from drillion.colors import WHITE
from drillion.entity import Entity
from drillion.maths import generate_circle_vertices, Polygon2
from drillion.physics_component import PhysicsComponent
from drillion.ship_control_component import ShipControlComponent
from drillion.ship_input_component import ShipInputComponent
from drillion.ship_keys import PLAYER_SHIP_KEYS
from drillion.sprite import PolygonSprite
from drillion.sprite_component import SpriteComponent
from drillion.transform_component import TransformComponent

class ShipEntityCreator(object):
    def __init__(self, input_update_phase, control_update_phase,
                 physics_update_phase, collision_transform_update_phase,
                 animation_update_phase, draw_phase, key_state_handler,
                 collision_detector, batch):
        self._input_update_phase = input_update_phase
        self._control_update_phase = control_update_phase
        self._physics_update_phase = physics_update_phase
        self._collision_transform_update_phase = \
            collision_transform_update_phase
        self._animation_update_phase = animation_update_phase

        self._draw_phase = draw_phase
        self._key_state_handler = key_state_handler
        self._collision_detector = collision_detector
        self._batch = batch

    def create(self, position=(0.0, 0.0), angle=0.0, color=WHITE,
               keys=PLAYER_SHIP_KEYS):
        vertices = generate_circle_vertices(3)
        polygon = Polygon2(vertices)

        transform_component = TransformComponent()
        physics_component = PhysicsComponent(transform_component,
                                             self._physics_update_phase,
                                             position=position, angle=angle)

        collision_body = CollisionBody(polygon)
        collision_component = CollisionComponent(transform_component,
                                                 self._collision_transform_update_phase,
                                                 collision_body,
                                                 self._collision_detector)

        control_component = ShipControlComponent(physics_component,
                                                 self._control_update_phase)
        input_component = ShipInputComponent(self._input_update_phase,
                                             control_component,
                                             self._key_state_handler, keys)

        vertices = generate_circle_vertices(3)
        sprite = PolygonSprite(vertices, color=color)
        sprite_component = SpriteComponent(sprite, self._batch)

        animation_component = AnimationComponent(transform_component,
                                                 sprite_component,
                                                 self._animation_update_phase,
                                                 self._draw_phase)

        components = [transform_component, physics_component,
                      collision_component, control_component, input_component,
                      sprite_component, animation_component]
        entity = Entity(components)
        collision_body.user_data = 'ship', entity
        return entity
