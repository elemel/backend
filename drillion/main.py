from drillion.block_entity_creator import BlockEntityCreator
from drillion.collision import CollisionDetector, CollisionListener
from drillion.colors import CYAN, WHITE, YELLOW
from drillion.draw_phase import DrawPhase
from drillion.game import Game
from drillion.pnoise import pnoise
from drillion.ship_keys import PLAYER_1_SHIP_KEYS, PLAYER_2_SHIP_KEYS
from drillion.ship_entity_creator import ShipEntityCreator
from drillion.update_phase import UpdatePhase

import pyglet
from pyglet.window import key
from pyglet.gl import *
import math
import random

class GameCollisionListener(CollisionListener):
    def __init__(self, game=None):
        self.game = game
        self.collisions = []

    def on_collision_add(self, collision):
        self.collisions.append(collision)

    def update(self, dt):
        for collision in self.collisions:
            for category, entity in [collision.body_a.user_data,
                                     collision.body_b.user_data]:
                if entity.key != -1:
                    self.game.remove_entity(entity)
        del self.collisions[:]

def main():
    pyglet.resource.path.append('../data')
    pyglet.resource.reindex()

    input_update_phase = UpdatePhase()
    control_update_phase = UpdatePhase()
    physics_update_phase = UpdatePhase()
    collision_transform_update_phase = UpdatePhase()
    collision_update_phase = UpdatePhase()
    animation_update_phase = UpdatePhase()

    collision_listener = GameCollisionListener()
    collision_detector = CollisionDetector(listener=collision_listener)
    collision_update_phase.add_handler(collision_detector)
    collision_update_phase.add_handler(collision_listener)

    draw_phase = DrawPhase()

    update_phases = [input_update_phase, control_update_phase,
                     physics_update_phase, collision_transform_update_phase,
                     collision_update_phase, animation_update_phase]
    draw_phases = [draw_phase]
    game = Game(update_phases, draw_phases)
    collision_listener.game = game

    ship_entity_creator = ShipEntityCreator(input_update_phase,
                                            control_update_phase,
                                            physics_update_phase,
                                            collision_transform_update_phase,
                                            animation_update_phase,
                                            draw_phase, game.key_state_handler,
                                            collision_detector, game.batch)

    block_entity_creator = BlockEntityCreator(collision_detector, game.batch)

    seed_x = random.random()
    seed_y = random.random()
    seed_z = random.random()

    noise_scale = 0.2

    for grid_x in xrange(-10, 10):
        for grid_y in xrange(-10, 10):
            if -2 <= grid_x < 2 and -1 <= grid_y < 1:
                continue
            noise_x = seed_x + noise_scale * float(grid_x)
            noise_y = seed_y + noise_scale * float(grid_y)
            noise_z = seed_z
            density = pnoise(noise_x, noise_y, noise_z)
            if density > 0.0:
                block_entity = block_entity_creator.create(grid_position=(grid_x, grid_y))
                game.add_entity(block_entity)

    ship_entity_1 = ship_entity_creator.create(position=(-2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=YELLOW,
                                               keys=PLAYER_1_SHIP_KEYS)
    game.add_entity(ship_entity_1)

    ship_entity_2 = ship_entity_creator.create(position=(2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               color=CYAN,
                                               keys=PLAYER_2_SHIP_KEYS)
    game.add_entity(ship_entity_2)

    pyglet.clock.schedule(game.update)
    pyglet.app.run()

if __name__ == '__main__':
    main()
