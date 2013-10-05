from backend.color import CYAN, WHITE, YELLOW
from backend.maths import generate_circle_vertices, Transform, Vector2
from backend.sprite import PolygonSprite

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

def fill_triangle(x1, y1, x2, y2, x3, y3, color=WHITE):
    pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
                         ('v2f', (x1, y1, x2, y2, x3, y3)),
                         ('c4B', 3 * color))

def fill_polygon(vertices, color=WHITE):
    vertex_data = []
    for v in vertices:
        vertex_data.extend(v)
    pyglet.graphics.draw(len(vertices), pyglet.gl.GL_POLYGON,
                         ('v2f', tuple(vertex_data)),
                         ('c4B', len(vertices) * color))

class UpdatePhase(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(handler):
        self._handlers.remove(handler)

    def update(self, dt):
        for handler in self._handlers:
            handler.update(dt)

class DrawPhase(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(handler):
        self._handlers.remove(handler)

    def draw(self):
        for handler in self._handlers:
            handler.draw()

class Component(object):
    def __init__(self):
        self.entity = None

    def create(self):
        pass

    def delete(self):
        pass

class Entity(object):
    def __init__(self):
        self.game = None
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def find_component(self, cls):
        for component in self.components:
            if isinstance(component, cls):
                return component
        return None

    def create(self):
        for component in self.components:
            component.entity = self
            component.create()

    def delete(self):
        for component in reversed(self.components):
            component.delete()
            component.entity = None

class Keyboard(object):
    def __init__(self):
        self.pressed_keys = set()

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

class TransformComponent(Component):
    def __init__(self):
        super(TransformComponent, self).__init__()
        self.transform = Transform()

class PhysicsComponent(Component):
    def __init__(self, transform_component, update_phase, position=(0.0, 0.0),
                 velocity=(0.0, 0.0), acceleration=(0.0, 0.0), angle=0.0,
                 angular_velocity=0.0, angular_acceleration=0.0):
        super(PhysicsComponent, self).__init__()

        self.position = Vector2(*position)
        self.velocity = Vector2(*velocity)
        self.acceleration = Vector2(*acceleration)

        self.angle = angle
        self.angular_velocity = angular_velocity
        self.angular_acceleration = angular_acceleration

        self.transform_component = transform_component
        self.update_phase = update_phase

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.add_handler(self)

    def update(self, dt):
        self.position += dt * self.velocity
        self.velocity += dt * self.acceleration

        self.angle += dt * self.angular_velocity
        self.angular_velocity += dt * self.angular_acceleration

        transform = self.transform_component.transform
        transform.reset()
        transform.rotate(self.angle)
        transform.translate(*self.position)
        self.transform_component.transform = transform

class SpriteComponent(Component):
    def __init__(self, sprite):
        super(SpriteComponent, self).__init__()
        self.sprite = sprite

    def create(self):
        self.sprite.batch = self.entity.game.batch

    def delete(self):
        self.sprite.batch = None

class AnimationComponent(Component):
    def __init__(self, transform_component, sprite_component, update_phase,
                 draw_phase):
        super(AnimationComponent, self).__init__()
        self.transform_component = transform_component
        self.sprite_component = sprite_component
        self.update_phase = update_phase
        self.draw_phase = draw_phase

    def create(self):
        self.update_phase.add_handler(self)
        self.draw_phase.add_handler(self)

    def delete(self):
        self.draw_phase.remove_handler(self)
        self.update_phase.remove_handler(self)

    def update(self, dt):
        pass

    def draw(self):
        self.sprite_component.sprite.transform = \
            self.transform_component.transform

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
    def __init__(self):
        super(Game, self).__init__(fullscreen=True)
        self.time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_phases = []
        self.draw_phases = []
        self.entities = []
        self.key_state_handler = pyglet.window.key.KeyStateHandler()

    def add_update_phase(self, phase):
        self.update_phases.append(phase)

    def remove_update_phase(self, phase):
        self.update_phases.remove(phase)

    def add_draw_phase(self, phase):
        self.draw_phases.append(phase)

    def remove_draw_phase(self, phase):
        self.draw_phases.remove(phase)

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
        for phase in self.update_phases:
            phase.update(dt)

    def on_draw(self):
        self.clear()
        self.draw_world()
        self.draw_hud()

    def draw_world(self):
        aspect_ratio = float(self.width) / float(self.height)
        half_width = aspect_ratio / self.camera_scale
        half_height = 1.0 / self.camera_scale

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-half_width, half_width, -half_height, half_height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        for phase in self.draw_phases:
            phase.draw()
        self.batch.draw()

    def draw_hud(self):
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
        entity = Entity()

        transform_component = TransformComponent()
        entity.add_component(transform_component)
        physics_component = PhysicsComponent(transform_component,
                                             self._physics_update_phase,
                                             position=position, angle=angle)
        entity.add_component(physics_component)
        control_component = ShipControlComponent(physics_component,
                                                 self._control_update_phase)
        entity.add_component(control_component)

        vertices = generate_circle_vertices(3)
        sprite = PolygonSprite(vertices, color=color)
        sprite_component = SpriteComponent(sprite)
        entity.add_component(sprite_component)

        animation_component = AnimationComponent(transform_component,
                                                 sprite_component,
                                                 self._animation_update_phase,
                                                 self._draw_phase)
        entity.add_component(animation_component)

        input_component = ShipKeyboardInputComponent(self._input_update_phase,
                                                     control_component,
                                                     self._key_state_handler,
                                                     keys)
        entity.add_component(input_component)

        return entity

class BoulderEntityCreator(object):
    def create(self, position=(0.0, 0.0)):
        entity = Entity()

        vertices = generate_circle_vertices(6)
        transform = Transform()
        transform.translate(*position)
        sprite = PolygonSprite(vertices, transform=transform)
        sprite_component = SpriteComponent(sprite)
        entity.add_component(sprite_component)

        return entity

def main():
    game = Game()

    input_update_phase = UpdatePhase()
    control_update_phase = UpdatePhase()
    physics_update_phase = UpdatePhase()
    animation_update_phase = UpdatePhase()

    game.add_update_phase(input_update_phase)
    game.add_update_phase(control_update_phase)
    game.add_update_phase(physics_update_phase)
    game.add_update_phase(animation_update_phase)

    draw_phase = DrawPhase()
    game.add_draw_phase(draw_phase)

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
