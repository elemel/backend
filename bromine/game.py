from bromine.bitmap_text import BitmapFont, BitmapFontConfig, BitmapLabel
from bromine.maths import mix
from bromine.shader import Shader

import pyglet
from pyglet.window import key
from pyglet.gl import *

class Game(pyglet.window.Window):
    def __init__(self, update_phases=[], draw_phases=[]):
        config = pyglet.gl.Config(double_buffer=1, sample_buffers=1,samples=16)
        super(Game, self).__init__(fullscreen=True, config=config)
        self.time = 0.0
        self.world_dt = 1.0 / 10.0
        self.world_time = 0.0
        self.camera_scale = 0.1
        self.batch = pyglet.graphics.Batch()
        self.update_phases = list(update_phases)
        self.draw_phases = list(draw_phases)
        self.entities = []
        self.key_state_handler = pyglet.window.key.KeyStateHandler()

        frag_shader_source = """
        uniform sampler2D tex;

        void main(void)
        {
            vec4 color = texture2D(tex, gl_TexCoord[0].st);
            vec3 rgb = vec3(1.0);
            float r = fwidth(color.a);
            float a = smoothstep(0.5 - r, 0.5 + r, color.a);
            gl_FragColor = vec4(rgb, a);
        }
        """
        self.glyph_shader = Shader(frag=[frag_shader_source])
        self.hud_batch = pyglet.graphics.Batch()
        self.glyph_image = pyglet.resource.image('font.png')
        self.glyph_texture = self.glyph_image.get_texture()

        self.font_config = BitmapFontConfig()
        self.font_config.load(pyglet.resource.file('font.txt'))
        self.font = BitmapFont(self.glyph_texture, self.font_config)
        self.label = BitmapLabel(self.font, text='BROMINE',
                                 batch=self.hud_batch)

        self.old_label_angle = 0.0
        self.label_angle = 0.0

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

            self.old_label_angle = self.label_angle
            self.label_angle += -0.01 * self.world_dt

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
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, float(self.width), 0.0, float(self.height), -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        label_angle = mix(self.old_label_angle, self.label_angle, alpha)

        label_transform = self.label.transform
        label_transform.reset()
        label_transform.scale(4.0, 4.0)
        label_transform.rotate(label_angle)
        label_transform.translate(0.5 * float(self.width), 0.5 * self.height)
        self.label.transform = label_transform

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(self.glyph_texture.target)
        glBindTexture(self.glyph_texture.target, self.glyph_texture.id)
        self.glyph_shader.bind()
        self.hud_batch.draw()
        self.glyph_shader.unbind()
        glDisable(self.glyph_texture.target)
        glDisable(GL_BLEND)
