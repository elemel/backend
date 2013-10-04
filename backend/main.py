from backend.color import CYAN, WHITE, YELLOW
from backend.maths import Transform, Vector2
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

def generate_circle_vertices(count, x=0.0, y=0.0, radius=1.0, angle=0.0):
    for i in xrange(count):
        a = angle + float(i) / float(count) * 2.0 * math.pi
        yield x + radius * math.cos(a), y + radius * math.sin(a)

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
    def __init__(self, transform_component):
        super(PhysicsComponent, self).__init__()

        self.position = Vector2()
        self.velocity = Vector2()
        self.acceleration = Vector2()

        self.angle = 0.0
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0

        self.transform_component = transform_component

    def create(self):
        self.entity.game.add_update_handler(self)

    def delete(self):
        self.entity.game.remove_update_handler(self)

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

class ShipComponent(Component):
    def __init__(self, transform_component, physics_component,
                 sprite_component, player_index):
        super(ShipComponent, self).__init__()
        self.player_index = player_index

        self.max_thrust_acceleration = 10.0
        self.max_turn_velocity = 2.0 * math.pi

        self.transform_component = transform_component
        self.physics_component = physics_component
        self.sprite_component = sprite_component

    def create(self):
        self.entity.game.update_handlers.append(self)
        self.entity.game.draw_handlers.append(self)

    def delete(self):
        self.entity.game.draw_handlers.remove(self)
        self.entity.game.update_handlers.remove(self)

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

    def draw(self):
        self.sprite_component.sprite.transform = \
            self.transform_component.transform

class Game(pyglet.window.Window):
    def __init__(self):
        super(Game, self).__init__(fullscreen=True)
        self.controls = [4 * [False], 4 * [False]]
        self.time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_handlers = []
        self.draw_handlers = []
        self.entities = []

    def add_update_handler(self, handler):
        self.update_handlers.append(handler)

    def remove_update_handler(self, handler):
        self.update_handlers.remove(handler)

    def add_draw_handler(self, handler):
        self.draw_handlers.append(handler)

    def remove_draw_handler(self, handler):
        self.draw_handlers.remove(handler)

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
        for handler in self.update_handlers:
            handler.update(dt)

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

        for handler in self.draw_handlers:
            handler.draw()
        self.batch.draw()

    def draw_hud(self):
        pass

def create_ship_entity(player_index=-1, x=0.0, y=0.0, angle=0.0, color=WHITE):
    entity = Entity()

    transform_component = TransformComponent()
    entity.add_component(transform_component)
    physics_component = PhysicsComponent(transform_component)
    entity.add_component(physics_component)

    vertices = generate_circle_vertices(3)
    sprite = PolygonSprite(vertices, color=color)
    sprite_component = SpriteComponent(sprite)
    entity.add_component(sprite_component)

    ship_component = ShipComponent(transform_component, physics_component,
                                   sprite_component, player_index)
    entity.add_component(ship_component)
    return entity

def create_boulder_entity(x=0.0, y=0.0):
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
    game.add_entity(create_ship_entity(player_index=0, x=-2.0,
                                       angle=(0.5 * math.pi), color=YELLOW))
    game.add_entity(create_ship_entity(player_index=1, x=2.0,
                                       angle=(0.5 * math.pi), color=CYAN))
    game.add_entity(create_boulder_entity(y=2.0))

    pyglet.clock.schedule(game.update)
    pyglet.app.run()
