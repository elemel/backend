from cavear.maths import Transform

class CollisionBody(object):
    def __init__(self, polygon, transform=Transform()):
        self.polygon = polygon
        self.transform = Transform(*transform)

    def touch(self):
        pass

class Collision(object):
    def __init__(self, body_a, body_b):
        self.body_a = body_a
        self.body_b = body_b

class CollisionListener(object):
    def on_collision_add(self, collision):
        pass

    def on_collision_remove(self, collision):
        pass

class CollisionDetector(object):
    def __init__(self, update_phase):
        self._bodies = []
        self._collisions = []
        self.listener = None

    def add_body(self, body):
        self._bodies.append(body)
        body.detector = self

    def remove_body(self, body):
        body.detector = None
        self._bodies.remove(body)

    def update(self, dt):
        for i in xrange(len(self._bodies) - 1):
            for j in xrange(i + 1, len(self._bodies)):
                
