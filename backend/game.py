import pyglet
from pyglet.window import key
from pyglet.gl import *

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
