from drillion.component import Component
from drillion.maths import clamp, mix, Vector2

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
        self.max_turn_acceleration = 8.0 * math.pi

        self.fire_time = 0.0
        self.cooldown_time = 0.05
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

        self.physics_component.angular_acceleration = \
            self.turn_control * self.max_turn_acceleration
        self.physics_component.angular_friction = \
            self.max_turn_acceleration * (1.0 - abs(self.turn_control))

        self.physics_component.acceleration = \
            (max(0.0, self.thrust_control) * self.max_thrust_acceleration *
             direction)
        self.physics_component.friction = \
            max(0.0, -self.thrust_control) * self.max_thrust_acceleration

        self.fire_time -= dt
        if self.fire_time < 0.0 and self.fire_control > 0.5:
            self.fire_time = self.cooldown_time

            position_x, position_y = self.physics_component.position
            angle = self.physics_component.angle
            normal_x = math.cos(angle)
            normal_y = math.sin(angle)
            tangent_x, tangent_y = -normal_y, normal_x

            position_offset = random.uniform(-0.5, 0.5)
            position_x += position_offset * tangent_x
            position_y += position_offset * tangent_y
            position = position_x, position_y

            bullet_velocity = self.bullet_velocity
            bullet_velocity += random.uniform(-0.5, 0.5)
            velocity_x, velocity_y = self.physics_component.velocity
            velocity_x += bullet_velocity * normal_x
            velocity_y += bullet_velocity * normal_y
            velocity = velocity_x, velocity_y

            bullet_entity = \
                self.bullet_entity_creator.create(position=position,
                                                  velocity=velocity)
            self.game.add_entity(bullet_entity)
