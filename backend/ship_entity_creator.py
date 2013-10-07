from backend.animation_component import AnimationComponent
from backend.color import WHITE
from backend.entity import Entity
from backend.maths import generate_circle_vertices
from backend.physics_component import PhysicsComponent
from backend.ship_control_component import ShipControlComponent
from backend.ship_input_component import ShipInputComponent
from backend.ship_keys import PLAYER_SHIP_KEYS
from backend.sprite import PolygonSprite
from backend.sprite_component import SpriteComponent
from backend.transform_component import TransformComponent

class ShipEntityCreator(object):
    def __init__(self, input_update_phase, control_update_phase,
                 physics_update_phase, animation_update_phase, draw_phase,
                 key_state_handler):
        self._input_update_phase = input_update_phase
        self._control_update_phase = control_update_phase
        self._physics_update_phase = physics_update_phase
        self._animation_update_phase = animation_update_phase

        self._draw_phase = draw_phase
        self._key_state_handler = key_state_handler

    def create(self, position=(0.0, 0.0), angle=0.0, color=WHITE,
               keys=PLAYER_SHIP_KEYS):
        transform_component = TransformComponent()
        physics_component = PhysicsComponent(transform_component,
                                             self._physics_update_phase,
                                             position=position, angle=angle)
        control_component = ShipControlComponent(physics_component,
                                                 self._control_update_phase)
        input_component = ShipInputComponent(self._input_update_phase,
                                             control_component,
                                             self._key_state_handler, keys)

        vertices = generate_circle_vertices(3)
        sprite = PolygonSprite(vertices, color=color)
        sprite_component = SpriteComponent(sprite)

        animation_component = AnimationComponent(transform_component,
                                                 sprite_component,
                                                 self._animation_update_phase,
                                                 self._draw_phase)

        components = [transform_component, physics_component,
                      control_component, input_component, sprite_component,
                      animation_component]
        return Entity(components)
