from backend.animation_component import AnimationComponent
from backend.color import CYAN, WHITE, YELLOW
from backend.component import Component
from backend.draw_phase import DrawPhase
from backend.entity import Entity
from backend.maths import generate_circle_vertices, Transform, Vector2
from backend.physics_component import PhysicsComponent
from backend.sprite import PolygonSprite
from backend.sprite_component import SpriteComponent
from backend.transform_component import TransformComponent
from backend.update_phase import UpdatePhase

import pyglet
from pyglet.window import key
from pyglet.gl import *
import math

PLAYER_SHIP_KEYS = dict(left=[key.A, key.LEFT], right=[key.D, key.RIGHT],
                        thrust=[key.W, key.UP], fire=[key.S, key.DOWN])
PLAYER_1_SHIP_KEYS = dict(left=[key.A], right=[key.D], thrust=[key.W],
                          fire=[key.S])
PLAYER_2_SHIP_KEYS = dict(left=[key.LEFT], right=[key.RIGHT],
                          thrust=[key.UP], fire=[key.DOWN])

class ShipKeyboardInputComponent(Component):
    def __init__(self, update_phase, control_component, key_state_handler,
                 keys=PLAYER_SHIP_KEYS):
        super(ShipKeyboardInputComponent, self).__init__()

        self._update_phase = update_phase
        self._control_component = control_component
        self._key_state_handler = key_state_handler

        self._left_keys = list(keys['left'])
        self._right_keys = list(keys['right'])
        self._thrust_keys = list(keys['thrust'])
        self._fire_keys = list(keys['fire'])

    def create(self):
        self._update_phase.add_handler(self)

    def delete(self):
        self._update_phase.remove_handler(self)

    def update(self, dt):
        left_control = self.get_control(self._left_keys)
        right_control = self.get_control(self._right_keys)
        thrust_control = self.get_control(self._thrust_keys)
        fire_control = self.get_control(self._fire_keys)

        turn_control = left_control - right_control

        self._control_component.turn_control = turn_control
        self._control_component.thrust_control = thrust_control

    def get_control(self, keys):
        for key in keys:
            if self._key_state_handler[key]:
                return 1.0
        return 0.0

class ShipControlComponent(Component):
    def __init__(self, physics_component, update_phase):
        super(ShipControlComponent, self).__init__()

        self.physics_component = physics_component
        self.update_phase = update_phase

        self.max_thrust_acceleration = 10.0
        self.max_turn_velocity = 2.0 * math.pi

        self.turn_control = 0.0
        self.thrust_control = 0.0

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.remove_handler(self)

    def update(self, dt):
        angle = self.physics_component.angle
        direction = Vector2(math.cos(angle), math.sin(angle))

        self.physics_component.angular_velocity = \
            self.turn_control * self.max_turn_velocity
        self.physics_component.acceleration = \
            self.thrust_control * self.max_thrust_acceleration * direction

class Game(pyglet.window.Window):
    def __init__(self, update_phases=[], draw_phases=[]):
        super(Game, self).__init__(fullscreen=True)
        self.time = 0.0
        self.world_dt = 1.0 / 10.0
        self.world_time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_phases = list(update_phases)
        self.draw_phases = list(draw_phases)
        self.entities = []
        self.key_state_handler = pyglet.window.key.KeyStateHandler()

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.game = self
        entity.create()

    def remove_entity(self, entity):
        entity.delete()
        entity.game = None
        self.entities.remove(entity)

    def on_key_press(self, symbol, modifiers):
        self.key_state_handler.on_key_press(symbol, modifiers)

        if symbol == key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        self.key_state_handler.on_key_release(symbol, modifiers)

    def update(self, dt):
        self.time += dt
        while self.time > self.world_time + self.world_dt:
            for phase in self.update_phases:
                phase.update(self.world_dt)
            self.world_time += self.world_dt

    def on_draw(self):
        alpha = (self.time - self.world_time) / self.world_dt
        self.clear()
        self.draw_world(alpha)
        self.draw_hud(alpha)

    def draw_world(self, alpha):
        aspect_ratio = float(self.width) / float(self.height)
        half_width = aspect_ratio / self.camera_scale
        half_height = 1.0 / self.camera_scale

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-half_width, half_width, -half_height, half_height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        for phase in self.draw_phases:
            phase.draw(alpha)
        self.batch.draw()

    def draw_hud(self, alpha):
        pass

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
        input_component = ShipKeyboardInputComponent(self._input_update_phase,
                                                     control_component,
                                                     self._key_state_handler,
                                                     keys)

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

class BoulderEntityCreator(object):
    def create(self, position=(0.0, 0.0)):
        vertices = generate_circle_vertices(6)
        transform = Transform()
        transform.translate(*position)
        sprite = PolygonSprite(vertices, transform=transform)
        sprite_component = SpriteComponent(sprite)
        return Entity([sprite_component])

def main():
    game = Game()

    input_update_phase = UpdatePhase()
    control_update_phase = UpdatePhase()
    physics_update_phase = UpdatePhase()
    animation_update_phase = UpdatePhase()

    draw_phase = DrawPhase()

    update_phases = [input_update_phase, control_update_phase,
                     physics_update_phase, animation_update_phase]
    draw_phases = [draw_phase]
    game = Game(update_phases, draw_phases)

    ship_entity_creator = ShipEntityCreator(input_update_phase,
                                            control_update_phase,
                                            physics_update_phase,
                                            animation_update_phase,
                                            draw_phase, game.key_state_handler)
    boulder_entity_creator = BoulderEntityCreator()

    ship_entity_1 = ship_entity_creator.create(position=(-2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=YELLOW,
                                               keys=PLAYER_1_SHIP_KEYS)
    game.add_entity(ship_entity_1)

    ship_entity_2 = ship_entity_creator.create(position=(2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=CYAN,
                                               keys=PLAYER_2_SHIP_KEYS)
    game.add_entity(ship_entity_2)

    boulder_entity = boulder_entity_creator.create(position=(0.0, 2.0))
    game.add_entity(boulder_entity)

    pyglet.clock.schedule(game.update)
    pyglet.app.run()

if __name__ == '__main__':
    main()
