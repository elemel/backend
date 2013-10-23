from drillion.maths import Transform2
from drillion.utils import flatten

import pyglet
from pyglet.gl import *

class BitmapFontConfig(object):
    def __init__(self):
        self.glyphs = {}
        self.image_size = 256, 256
        self.glyph_size = 16, 16

    def load(self, file_obj):
        image_width, image_height = self.image_size
        glyph_width, glyph_height = self.glyph_size
        lines = (line for line in file_obj if line.strip())
        for y, line in enumerate(lines):
            for x, name in enumerate(line.split()):
                s1 = float(x * glyph_width) / float(image_width)
                t1 = float(y * glyph_height) / float(image_height)
                s2 = float((x + 1) * glyph_width) / float(image_width)
                t2 = float((y + 1) * glyph_height) / float(image_height)
                self.glyphs[name] = (s1, 1.0 - t2), (s2, 1.0 - t1)

class BitmapFont(object):
    def __init__(self, texture, config):
        self.texture = texture
        self.config = config

    @property
    def glyph_size(self):
        width, height = self.config.glyph_size
        return float(width), float(height)

    def get_glyph_tex_coords(self, name):
        return self.config.glyphs[name]

class BitmapLabel(object):
    def __init__(self, font, text='', alignment=(0.0, 0.0),
                 transform=Transform2(), group=None, batch=None):
        self._font = font
        self._text = text
        self._alignment = alignment
        self._transform = Transform2(*transform)
        self._vertex_list = None
        self._group = None
        self._batch = None
        self.group = group
        self.batch = batch

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._update_vertex_list()

    @property
    def alignment(self):
        return self._alignment

    @alignment.setter
    def aligment(self, alignment):
        self._alignment = alignment
        self._update_vertex_list()

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, transform):
        self._transform.assign(*transform)
        self._update_vertex_list()

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group):
        if group is not self._group:
            if self._batch is not None:
                self._batch.migrate(self._vertex_list, GL_QUADS,
                                    self._group, self._batch)
            self._group = group

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, batch):
        if batch is not self._batch:
            if self._batch is not None:
                if batch is not None:
                    self._batch.migrate(self._vertex_list, GL_QUADS,
                                        self._group, batch)
                else:
                    self._vertex_list.delete()
                    self._vertex_list = None
            else:
                vertex_count = 4 * len(self._text)
                vertex_data = tuple(self._generate_vertex_data())
                tex_coord_data = tuple(self._generate_tex_coord_data())
                self._vertex_list = batch.add(vertex_count, GL_QUADS,
                                              self._group,
                                              ('v2f', vertex_data),
                                              ('t2f', tex_coord_data))
            self._batch = batch

    def _update_vertex_list(self):
        if self._vertex_list is not None:
            self._vertex_list.vertices = tuple(self._generate_vertex_data())
            self._vertex_list.tex_coords = tuple(self._generate_tex_coord_data())

    def _generate_vertex_data(self):
        return flatten(self._generate_vertices())

    def _generate_vertices(self):
        sx, sy = self._font.glyph_size

        ax, ay = self.alignment
        tx = -0.5 * (ax + 1.0) * float(len(self._text))
        ty = -0.5 * (ay + 1.0)

        for x, y in self._generate_raw_vertices():
            yield self._transform.transform_point(sx * (x + tx), sy * (y + ty))

    def _generate_raw_vertices(self):
        for i in xrange(len(self._text)):
            yield float(i), 0.0
            yield float(i + 1), 0.0
            yield float(i + 1), 1.0
            yield float(i), 1.0

    def _generate_tex_coord_data(self):
        return flatten(self._generate_tex_coords())

    def _generate_tex_coords(self):
        for char in self._text:
            (s1, t1), (s2, t2) = self._font.get_glyph_tex_coords(char)
            yield s1, t1
            yield s2, t1
            yield s2, t2
            yield s1, t2
