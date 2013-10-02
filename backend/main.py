from backend.color import WHITE
from backend.maths import Transform
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

class Entity(object):
    def __init__(self):
        self.window = None

    def create(self):
        pass

    def delete(self):
        pass

class Ship(Entity):
    def __init__(self, player_index=-1, x=0.0, y=0.0, angle=0.0):
        super(Ship, self).__init__()
        self.player_index = player_index
        self.x = x
        self.y = y
        self.angle = angle
        self.transform = Transform()
        vertices = generate_circle_vertices(3, angle=(0.5 * math.pi))
        self.sprite = PolygonSprite(vertices)

    def create(self):
        self.sprite.batch = self.window.batch
        self.window.update_handlers.append(self)
        self.window.draw_handlers.append(self)

    def delete(self):
        self.window.draw_handlers.remove(self)
        self.window.update_handlers.remove(self)
        self.sprite.batch = None

    def update(self, dt):
        self.angle += dt
        self.transform.reset()
        self.transform.translate(self.x, self.y)
        self.transform.rotate(self.angle)

    def draw(self):
        self.sprite.transform = self.transform

class Boulder(Entity):
    def __init__(self, x=0.0, y=0.0):
        vertices = generate_circle_vertices(6)
        transform = Transform()
        transform.translate(x, y)
        self.sprite = PolygonSprite(vertices, transform=transform)

    def create(self):
        self.sprite.batch = self.window.batch

    def delete(self):
        self.sprite.batch = None

class BackendWindow(pyglet.window.Window):
    def __init__(self):
        super(BackendWindow, self).__init__(fullscreen=True)
        self.controls = [4 * [False], 4 * [False]]
        self.time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_handlers = []
        self.draw_handlers = []
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.window = self
        entity.create()

    def remove_entity(self, entity):
        entity.delete()
        entity.window = None
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

if __name__ == '__main__':
    backend_window = BackendWindow()
    backend_window.add_entity(Ship())
    backend_window.add_entity(Boulder(x=3.0))
    pyglet.clock.schedule(backend_window.update)
    pyglet.app.run()
