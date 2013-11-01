from drillion.component import Component
from drillion.maths import Vector2

import math
import random

class ShipControlComponent(Component):
    def __init__(self, physics_component, update_phase, bullet_entity_creator,
                 game):
        super(ShipControlComponent, self).__init__()

        self.physics_component = physics_component
        self.update_phase = update_phase
        self.bullet_entity_creator = bullet_entity_creator
        self.game = game

        self.max_thrust_acceleration = 10.0
        self.max_turn_velocity = 2.0 * math.pi

        self.fire_time = 0.0
        self.cooldown_time = 0.1
        self.bullet_velocity = 10.0

        self.turn_control = 0.0
        self.thrust_control = 0.0
        self.fire_control = 0.0

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

        self.fire_time -= dt
        if self.fire_time < 0.0 and self.fire_control > 0.5:
            self.fire_time = self.cooldown_time
            position = self.physics_component.position
            angle = self.physics_component.angle
            angle += random.uniform(-0.1, 0.1)
            angle_x = math.cos(angle)
            angle_y = math.sin(angle)
            velocity_x, velocity_y = self.physics_component.velocity
            velocity_x += self.bullet_velocity * angle_x
            velocity_y += self.bullet_velocity * angle_y
            velocity = velocity_x, velocity_y
            bullet_entity = \
                self.bullet_entity_creator.create(position=position,
                                                  velocity=velocity)
            self.game.add_entity(bullet_entity)
