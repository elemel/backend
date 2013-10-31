import math

def clamp(x, x1, x2):
    return min(max(x, x1), x2)

def cf2ub(cf):
    return clamp(int(cf * 256.0), 0, 255)

def mix(x1, x2, t):
    return x1 + t * (x2 - x1)

def generate_circle_vertices(count, x=0.0, y=0.0, radius=1.0, angle=0.0):
    for i in xrange(count):
        a = angle + float(i) / float(count) * 2.0 * math.pi
        yield x + radius * math.cos(a), y + radius * math.sin(a)

class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __setitem__(self, index, value):
        values = [self.x, self.y]
        values[index] = value
        self.x, self.y = values

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __iadd__(self, other):
        x, y = other
        self.x += x
        self.y += y
        return self

    def __add__(self, other):
        x, y = other
        return Vector2(self.x + x, self.y + y)

    def __isub__(self, other):
        x, y = other
        self.x -= x
        self.y -= y
        return self

    def __sub__(self, other):
        x, y = other
        return Vector2(self.x - x, self.y - y)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vector2(other * self.x, other * self.y)

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __str__(self):
        return str([self.x, self.y])

    def assign(self, x, y):
        self.x = x
        self.y = y

class Transform2(object):
    def __init__(self, a=1.0, b=0.0, c=0.0, d=0.0, e=1.0, f=0.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def __iter__(self):
        return iter([self.a, self.b, self.c, self.d, self.e, self.f])

    def assign(self, a, b, c, d, e, f):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def reset(self):
        self.assign(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def multiply(self, a, b, c, d, e, f):
        self.assign(self.a * a + self.b * d,
                    self.a * b + self.b * e,
                    self.a * c + self.b * f + self.c,
                    self.d * a + self.e * d,
                    self.d * b + self.e * e,
                    self.d * c + self.e * f + self.f)

    def right_multiply(self, a, b, c, d, e, f):
        self.assign(a * self.a + b * self.d,
                    a * self.b + b * self.e,
                    a * self.c + b * self.f + c,
                    d * self.a + e * self.d,
                    d * self.b + e * self.e,
                    d * self.c + e * self.f + f)

    def translate(self, x, y):
        self.c += x
        self.f += y

    def rotate(self, angle):
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        self.multiply(cos_angle, -sin_angle, 0.0, sin_angle, cos_angle, 0.0)

    def scale(self, scale_x, scale_y):
        self.multiply(scale_x, 0.0, 0.0, 0.0, scale_y, 0.0)

    def transform_vector(self, x, y):
        return self.a * x + self.b * y, self.d * x + self.e * y

    def transform_point(self, x, y):
        return (self.a * x + self.b * y + self.c,
                self.d * x + self.e * y + self.f)

    def mix(self, source, target, alpha):
        self.assign(mix(source.a, target.a, alpha),
                    mix(source.b, target.b, alpha),
                    mix(source.c, target.c, alpha),
                    mix(source.d, target.d, alpha),
                    mix(source.e, target.e, alpha),
                    mix(source.f, target.f, alpha))

def cross_2(x1, y1, x2, y2):
    return x1 * y2 - x2 * y1

class Box2(object):
    def __init__(self, p1=(-1.0, -1.0), p2=(1.0, 1.0)):
        self.p1 = Vector2(*p1)
        self.p2 = Vector2(*p2)

    @property
    def center(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        return 0.5 * (x1 + x2), 0.5 * (y1 + y2)

    @property
    def size(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        return x2 - x1, y2 - y1

    def reset(self):
        self.p1.assign(-1.0, -1.0)
        self.p2.assign(1.0, 1.0)

    def clear(self):
        self.p1.assign(float('inf'), float('inf'))
        self.p2.assign(float('-inf'), float('-inf'))

    def add_point(self, x, y):
        self.p1.x = min(self.p1.x, x)
        self.p1.y = min(self.p1.y, y)
        self.p2.x = max(self.p2.x, x)
        self.p2.y = max(self.p2.y, y)

    def intersects(self, shape):
        return shape.intersects_box(self)

    def intersects_box(self, box):
        return (self.p1.x < box.p2.x and box.p1.x < self.p2.x and
                self.p1.y < box.p2.y and box.p1.y < self.p2.y)

    def contains_point(self, x, y):
        return self.p1.x < x < self.p2.x and self.p1.y < y < self.p2.y

    def __str__(self):
        return '[%s, %s]', (self.p1, self.p2)

class Polygon2(object):
    def __init__(self, vertices=[]):
        self.vertices = list(Vector2(x, y) for x, y in vertices)

    def __len__(self):
        return len(self.vertices)

    def __iter__(self):
        return iter(self.vertices)

    def __getitem__(self, index):
        return self.vertices[index]

    def __setitem__(self, index, vertex):
        self.vertices[index].assign(*vertex)

    @property
    def edges(self):
        for i in xrange(len(self.vertices) - 1):
            yield self.vertices[i], self.vertices[i + 1]
        yield self.vertices[-1], self.vertices[0]

    def intersects(self, other):
        return other.intersects_polygon(self)

    def intersects_polygon(self, other):
        return (not self._separates_polygon(other) and
                not other._separates_polygon(self))

    def _separates_polygon(self, polygon):
        return any(self._edge_separates_polygon(x1, y1, x2, y2, polygon)
                   for (x1, y1), (x2, y2) in self.edges)

    def _edge_separates_polygon(self, edge_x1, edge_y1, edge_x2, edge_y2,
                                polygon):
        return not any(self._edge_contains_point(edge_x1, edge_y1,
                                                 edge_x2, edge_y2, x, y)
                       for x, y in polygon)

    def contains_point(self, x, y):
        return all(self._edge_contains_point(p1.x, p1.y, p2.x, p2.y, x, y)
                   for p1, p2 in self.edges)

    def _edge_contains_point(self, edge_x1, edge_y1, edge_x2, edge_y2,
                             point_x, point_y):
        return (cross_2(point_x - edge_x1, point_y - edge_y1,
                        edge_x2 - edge_x1, edge_y2 - edge_y1) < 0.0)
