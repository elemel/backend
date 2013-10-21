from bromine.colors import WHITE
from bromine.maths import Transform2
from bromine.utils import flatten

import pyglet
from pyglet.gl import *

class PolygonSprite(object):
    def __init__(self, vertices=[], color=WHITE, transform=Transform2(),
                 group=None, batch=None):
        self._vertices = list(vertices)
        self._color = color
        self._transform = Transform2(*transform)
        self._vertex_list = None
        self._group = None
        self._batch = None
        self.group = group
        self.batch = batch

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        self._vertices = list(vertices)
        self._update_vertex_list()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
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
            self._delete_vertex_list()
            self._group = group
            self._create_vertex_list()

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, batch):
        if batch is not self._batch:
            self._delete_vertex_list()
            self._batch = batch
            self._create_vertex_list()

    def _create_vertex_list(self):
        if self._vertex_list is None and self._batch is not None:
            vertex_count = len(self.vertices)
            indices = tuple(flatten((0, i, i + 1)
                                    for i in xrange(1, vertex_count - 1)))
            vertex_data = tuple(flatten(self.transform.transform_point(*v)
                                        for v in self.vertices))
            color_data = len(self.vertices) * self.color
            self._vertex_list = self._batch.add_indexed(vertex_count,
                                                        GL_TRIANGLES,
                                                        self._group, indices,
                                                        ('v2f', vertex_data),
                                                        ('c4B', color_data))

    def _delete_vertex_list(self):
        if self._vertex_list is not None:
            self._vertex_list.delete()
            self._vertex_list = None

    def _update_vertex_list(self):
        if self._vertex_list is not None:
            vertex_data = tuple(flatten(self.transform.transform_point(*v)
                                        for v in self.vertices))
            self._vertex_list.vertices = vertex_data
            self._vertex_list.colors = len(self.vertices) * self.color
