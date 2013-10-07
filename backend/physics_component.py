from backend.component import Component
from backend.maths import Vector2

class PhysicsComponent(Component):
    def __init__(self, transform_component, update_phase, position=(0.0, 0.0),
                 velocity=(0.0, 0.0), acceleration=(0.0, 0.0), angle=0.0,
                 angular_velocity=0.0, angular_acceleration=0.0):
        super(PhysicsComponent, self).__init__()

        self.position = Vector2(*position)
        self.velocity = Vector2(*velocity)
        self.acceleration = Vector2(*acceleration)

        self.angle = angle
        self.angular_velocity = angular_velocity
        self.angular_acceleration = angular_acceleration

        self.transform_component = transform_component
        self.update_phase = update_phase

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.add_handler(self)

    def update(self, dt):
        self.position += dt * self.velocity
        self.velocity += dt * self.acceleration

        self.angle += dt * self.angular_velocity
        self.angular_velocity += dt * self.angular_acceleration

        transform = self.transform_component.transform
        transform.reset()
        transform.rotate(self.angle)
        transform.translate(*self.position)
        self.transform_component.transform = transform
