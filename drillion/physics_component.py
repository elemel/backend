from drillion.component import Component
from drillion.maths import clamp, sign, Transform2, Vector2

from math import pi, sqrt

class PhysicsComponent(Component):
    def __init__(self, transform_component, update_phase, position=(0.0, 0.0),
                 velocity=(0.0, 0.0), acceleration=(0.0, 0.0),
                 max_velocity=1.0, friction=0.0, angle=0.0,
                 angular_velocity=0.0, angular_acceleration=0.0,
                 max_angular_velocity=(2.0 * pi), angular_friction=0.0):
        super(PhysicsComponent, self).__init__()

        self.position = tuple(position)
        self.velocity = tuple(velocity)
        self.acceleration = tuple(acceleration)
        self.max_velocity = max_velocity
        self.friction = friction

        self.angle = angle
        self.angular_velocity = angular_velocity
        self.angular_acceleration = angular_acceleration
        self.max_angular_velocity = max_angular_velocity
        self.angular_friction = angular_friction

        self.transform_component = transform_component
        self.update_phase = update_phase

        self._transform = Transform2()
        self._update_transform()

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.add_handler(self)

    def update(self, dt):
        x, y = self.position
        dx, dy = self.velocity
        ddx, ddy = self.acceleration

        dx += dt * ddx
        dy += dt * ddy

        if self.friction > 0.0 or \
                dx * dx + dy * dy > self.max_velocity * self.max_velocity:
            velocity = sqrt(dx * dx + dy * dy)
            if velocity > 0.0:
                dx /= velocity
                dy /= velocity
            velocity = clamp(velocity - dt * self.friction, 0.0,
                             self.max_velocity)
            dx *= velocity
            dy *= velocity

        x += dt * dx
        y += dt * dy

        self.position = x, y
        self.velocity = dx, dy

        self.angular_velocity += dt * self.angular_acceleration

        self.angular_velocity = (sign(self.angular_velocity) *
                                 max(0.0, abs(self.angular_velocity) -
                                          dt * self.angular_friction))

        self.angular_velocity = clamp(self.angular_velocity,
                                      -self.max_angular_velocity,
                                      self.max_angular_velocity)

        self.angle += dt * self.angular_velocity

        self._update_transform()

    def _update_transform(self):
        self._transform.reset()
        if self.angle != 0.0:
            self._transform.rotate(self.angle)
        self._transform.translate(*self.position)
        self.transform_component.transform = self._transform
