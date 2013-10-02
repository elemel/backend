import math

class Transform(object):
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
        self.assign(self.a * a + self.b * d + self.c,
                    self.a * b + self.b * e + self.c,
                    self.a * c + self.b * f + self.c,
                    self.d * a + self.e * d + self.f,
                    self.d * b + self.e * e + self.f,
                    self.d * c + self.e * f + self.f)

    def right_multiply(self, a, b, c, d, e, f):
        self.assign(a * self.a + b * self.d + c,
                    a * self.b + b * self.e + c,
                    a * self.c + b * self.f + c,
                    d * self.a + e * self.d + f,
                    d * self.b + e * self.e + f,
                    d * self.c + e * self.f + f)

    def translate(self, x, y):
        self.c += x
        self.f += y

    def rotate(self, angle):
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        self.multiply(cos_angle, -sin_angle, 0.0, sin_angle, cos_angle, 0.0)

    def scale(self, scale_x, scale_y):
        self.multiply(scale_x, scale_x, 0.0, scale_y, scale_y, 0.0)

    def transform_vector(self, x, y):
        return self.a * x + self.b * y, self.d * x + self.e * y

    def transform_point(self, x, y):
        return (self.a * x + self.b * y + self.c,
                self.d * x + self.e * y + self.f)
