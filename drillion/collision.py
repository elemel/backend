from drillion.maths import Box2, Polygon2, Transform2

from collections import defaultdict
from math import floor

class CollisionBody(object):
    def __init__(self, polygon, transform=Transform2(), user_data=None):
        self._polygon = Polygon2(polygon)
        self._transform = Transform2(*transform)
        self.user_data = user_data
        self._detector = None
        self._key = -1
        self._collisions = []
        self._world_polygon = Polygon2(polygon)
        self._world_bounds = Box2()
        self._grid_bounds = (0, 0), (0, 0)
        self._dirty = False

    @property
    def key(self):
        return self._key

    @property
    def transform(self):
        return self._transform

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
        body._grid_bounds = self._get_grid_bounds(body._world_bounds)
        (grid_x1, grid_y1), (grid_x2, grid_y2) = body._grid_bounds
        for grid_x in xrange(grid_x1, grid_x2):
            for grid_y in xrange(grid_y1, grid_y2):
                self._cells[grid_x, grid_y].append(body)

    def remove_body(self, body):
        (grid_x1, grid_y1), (grid_x2, grid_y2) = body._grid_bounds
        for grid_x in xrange(grid_x1, grid_x2):
            for grid_y in xrange(grid_y1, grid_y2):
                self._cells[grid_x, grid_y].remove(body)

    def update_body(self, body):
        grid_bounds = self._get_grid_bounds(body._world_bounds)
        if grid_bounds != body._grid_bounds:
            self.remove_body(body)
            self.add_body(body)

    def _get_grid_bounds(self, bounds):
        x1, y1 = bounds.p1
        x2, y2 = bounds.p2
        grid_x1 = int(floor(x1 / self._cell_size))
        grid_y1 = int(floor(y1 / self._cell_size))
        grid_x2 = int(floor(x2 / self._cell_size)) + 1
        grid_y2 = int(floor(y2 / self._cell_size)) + 1
        return (grid_x1, grid_y1), (grid_x2, grid_y2)

    def find_collisions(self, body):
        bounds = body._world_bounds
        (grid_x1, grid_y1), (grid_x2, grid_y2) = body._grid_bounds
        collisions = set()
        for grid_x in xrange(grid_x1, grid_x2):
            for grid_y in xrange(grid_y1, grid_y2):
                collisions.update(self._cells[grid_x, grid_y])
        for other_body in collisions:
            if other_body is not body and \
                    bounds.intersects(other_body._world_bounds):
                yield other_body

class CollisionDetector(object):
    def __init__(self, listener=None):
        self._grid = CollisionGrid(2.0)
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

        body._dirty = True
        self._dirty_bodies.append(body)
        body._grid_bounds = (0, 0), (0, 0)

    def remove_body(self, body):
        self._grid.remove_body(body)

        if body._dirty:
            self._dirty_bodies.remove(body)
        body._key = -1
        body._detector = None
        self._bodies.remove(body)

    def update(self, dt):
        collisions = []
        while self._dirty_bodies:
            body = self._dirty_bodies.pop()
            body._dirty = False

            body._update_world_geometry()
            self._grid.update_body(body)

            for other_body in self._grid.find_collisions(body):
                if not other_body._dirty and \
                    body._world_polygon.intersects(other_body._world_polygon):
                    if body.user_data < other_body.user_data:
                        collision = Collision(body, other_body)
                    else:
                        collision = Collision(other_body, body)
                    collisions.append(collision)
        if self._listener is not None:
            for collision in collisions:
                self._listener.on_collision_add(collision)
                self._listener.on_collision_remove(collision)
