from backend.color import CYAN, WHITE, YELLOW
from backend.maths import generate_circle_vertices, Transform, Vector2
from backend.sprite import PolygonSprite

import pyglet
from pyglet.window import key
from pyglet.gl import *
import math

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

KEYS = {
    key.W: (0, UP),
    key.A: (0, LEFT),
    key.S: (0, DOWN),
    key.D: (0, RIGHT),

    key.UP: (1, UP),
    key.LEFT: (1, LEFT),
    key.DOWN: (1, DOWN),
    key.RIGHT: (1, RIGHT),
}

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
    def __init__(self, physics_component, player_index, update_phase):
        super(ShipControlComponent, self).__init__()
        self.player_index = player_index

        self.max_thrust_acceleration = 10.0
        self.max_turn_velocity = 2.0 * math.pi

        self.physics_component = physics_component
        self.update_phase = update_phase

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.remove_handler(self)

    def update(self, dt):
        thrust_control = 0.0
        turn_control = 0.0

        if self.player_index != -1:
            controls = self.entity.game.controls[self.player_index]
            turn_control = float(controls[1]) - float(controls[3])
            thrust_control = float(controls[0])

        angle = self.physics_component.angle
        direction = Vector2(math.cos(angle), math.sin(angle))

        self.physics_component.angular_velocity = \
            turn_control * self.max_turn_velocity
        self.physics_component.acceleration = \
            thrust_control * self.max_thrust_acceleration * direction

class Game(pyglet.window.Window):
    def __init__(self):
        super(Game, self).__init__(fullscreen=True)
        self.controls = [4 * [False], 4 * [False]]
        self.time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_phases = []
        self.draw_phases = []
        self.entities = []

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
        if symbol == key.ESCAPE:
            self.close()
        if symbol in KEYS:
            player_index, control_index = KEYS[symbol]
            self.controls[player_index][control_index] = True

    def on_key_release(self, symbol, modifiers):
        if symbol in KEYS:
            player_index, control_index = KEYS[symbol]
            self.controls[player_index][control_index] = False

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
    def __init__(self, update_phase, draw_phase):
        self._update_phase = update_phase
        self._draw_phase = draw_phase

    def create(self, player_index=-1, position=(0.0, 0.0), angle=0.0,
               color=WHITE):
        entity = Entity()

        transform_component = TransformComponent()
        entity.add_component(transform_component)
        physics_component = PhysicsComponent(transform_component, update_phase,
                                             position=position, angle=angle)
        entity.add_component(physics_component)
        control_component = ShipControlComponent(physics_component, player_index,
                                                 update_phase)
        entity.add_component(control_component)

        vertices = generate_circle_vertices(3)
        sprite = PolygonSprite(vertices, color=color)
        sprite_component = SpriteComponent(sprite)
        entity.add_component(sprite_component)

        animation_component = AnimationComponent(transform_component,
                                                 sprite_component, update_phase,
                                                 draw_phase)
        entity.add_component(animation_component)

        return entity

def create_boulder_entity(update_phase, draw_phase, x=0.0, y=0.0):
    entity = Entity()

    vertices = generate_circle_vertices(6)
    transform = Transform()
    transform.translate(x, y)
    sprite = PolygonSprite(vertices, transform=transform)
    sprite_component = SpriteComponent(sprite)
    entity.add_component(sprite_component)

    return entity

if __name__ == '__main__':
    game = Game()

    update_phase = UpdatePhase()
    game.add_update_phase(update_phase)

    draw_phase = DrawPhase()
    game.add_draw_phase(draw_phase)

    ship_entity_creator = ShipEntityCreator(update_phase, draw_phase)

    ship_entity_1 = ship_entity_creator.create(player_index=0,
                                               position=(-2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=YELLOW)
    game.add_entity(ship_entity_1)

    ship_entity_2 = ship_entity_creator.create(player_index=1,
                                               position=(2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=CYAN)
    game.add_entity(ship_entity_2)

    game.add_entity(create_boulder_entity(game.update_phases[0],
                                          game.draw_phases[0], y=2.0))

    pyglet.clock.schedule(game.update)
    pyglet.app.run()
