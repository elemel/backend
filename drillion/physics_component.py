from drillion.component import Component
from drillion.maths import Transform2, Vector2

class PhysicsComponent(Component):
    def __init__(self, transform_component, update_phase, position=(0.0, 0.0),
                 velocity=(0.0, 0.0), acceleration=(0.0, 0.0), angle=0.0,
                 angular_velocity=0.0, angular_acceleration=0.0):
        super(PhysicsComponent, self).__init__()

        self.position = tuple(position)
        self.velocity = tuple(velocity)
        self.acceleration = tuple(acceleration)

        self.angle = angle
        self.angular_velocity = angular_velocity
        self.angular_acceleration = angular_acceleration

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

        x += dt * dx
        y += dt * dy
        dx += dt * ddx
        dy += dt * ddy

        self.angle += dt * self.angular_velocity
        self.angular_velocity += dt * self.angular_acceleration

        self.position = x, y
        self.velocity = dx, dy

        self._update_transform()

    def _update_transform(self):
        self._transform.reset()
        if self.angle != 0.0:
            self._transform.rotate(self.angle)
        self._transform.translate(*self.position)
        self.transform_component.transform = self._transform
