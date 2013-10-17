from bromine.component import Component
from bromine.maths import Vector2

import math

class ShipControlComponent(Component):
    def __init__(self, physics_component, update_phase):
        super(ShipControlComponent, self).__init__()

        self.physics_component = physics_component
        self.update_phase = update_phase

        self.max_thrust_acceleration = 10.0
        self.max_turn_velocity = 2.0 * math.pi

        self.turn_control = 0.0
        self.thrust_control = 0.0

    def create(self):
        self.update_phase.add_handler(self)

    def delete(self):
        self.update_phase.remove_handler(self)

    def update(self, dt):
        angle = self.physics_component.angle
        direction = Vector2(math.cos(angle), math.sin(angle))

        self.physics_component.angular_velocity = \
            self.turn_control * self.max_turn_velocity
        self.physics_component.acceleration = \
            self.thrust_control * self.max_thrust_acceleration * direction
