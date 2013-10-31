from drillion.maths import Box2, Polygon2, Transform2

from collections import defaultdict
from math import floor

class CollisionBody(object):
    def __init__(self, polygon, transform=Transform2(), seed=False,
                 user_data=None):
        self._polygon = Polygon2(polygon)
        self._transform = Transform2(*transform)
        self._seed = seed
        self.user_data = user_data
        self._detector = None
        self._key = -1
        self._collisions = []
        self._world_polygon = Polygon2(polygon)
        self._world_bounds = Box2()
        self._grid_position = 0, 0
        self._dirty = True

    @property
    def key(self):
        return self._key

    @property
    def transform(self):
        return self._transform

    @property
    def seed(self):
        return self._seed

    @property
    def dirty(self):
        return self._dirty

    def touch(self):
        if not self._dirty:
            if self._detector is not None:
                self._detector._dirty_bodies.append(self)
            self._dirty = True

    def _update_world_geometry(self):
        self._world_bounds.clear()
        for vertex, world_vertex in zip(self._polygon, self._world_polygon):
            world_vertex.assign(*self._transform.transform_point(*vertex))
            self._world_bounds.add_point(*world_vertex)

    def __str__(self):
        return '#%d' % self._key

class Collision(object):
    def __init__(self, body_a, body_b, user_data=None):
        self.body_a = body_a
        self.body_b = body_b
        self.user_data = user_data

    def __str__(self):
        return '%s %s' % (self.body_a, self.body_b)

class CollisionListener(object):
    def on_collision_add(self, collision):
        pass

    def on_collision_remove(self, collision):
        pass

class CollisionGrid(object):
    def __init__(self, cell_size=1.0):
        self._cell_size = cell_size
        self._cells = defaultdict(list)

    def add_body(self, body):
        body._grid_position = self._get_grid_position(body._world_bounds.center)
        self._cells[body._grid_position].append(body)

    def remove_body(self, body):
        self._cells[body._grid_position].remove(body)

    def _get_grid_position(self, position):
        x, y = position
        return int(floor(x / self._cell_size)), int(floor(y / self._cell_size))

    def find_collisions(self, body):
        grid_x, grid_y = body._grid_position
        bounds = body._world_bounds
        for i in xrange(grid_x - 1, grid_x + 2):
            for j in xrange(grid_y - 1, grid_y + 2):
                for other_body in self._cells[i, j]:
                    if other_body is not body and \
                        bounds.intersects(other_body._world_bounds):
                        yield other_body

class CollisionDetector(object):
    def __init__(self, listener=None):
        self._grid = CollisionGrid(5.0)
        self._bodies = []
        self._dirty_bodies = []
        self._collisions = []
        self._listener = listener
        self._next_key = 0

    def add_body(self, body):
        self._bodies.append(body)
        body._detector = self
        body._key = self._next_key
        self._next_key += 1

        if body._dirty:
            body._update_world_geometry()
            body._dirty = False
        self._grid.add_body(body)

    def remove_body(self, body):
        self._grid.remove_body(body)

        if body._dirty:
            self._dirty_bodies.remove(body)
            body._dirty = False
        body._key = -1
        body._detector = None
        self._bodies.remove(body)

    def update(self, dt):
        for body in self._dirty_bodies:
            body._update_world_geometry()
            self._grid.remove_body(body)
            self._grid.add_body(body)
            body._dirty = False
        del self._dirty_bodies[:]

        for i, body_i in enumerate(self._bodies):
            if not body_i.seed:
                continue

            for j, body_j in enumerate(self._grid.find_collisions(body_i)):
                if not body_j.seed or i < j:
                    polygon_i = body_i._world_polygon
                    polygon_j = body_j._world_polygon
                    if polygon_i.intersects(polygon_j):
                        collision = Collision(body_i, body_j)
                        if self._listener is not None:
                            self._listener.on_collision_add(collision)
                            self._listener.on_collision_remove(collision)
