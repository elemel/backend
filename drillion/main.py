from drillion.block_entity_creator import BlockEntityCreator
from drillion.block_bullet_collision_handler import BlockBulletCollisionHandler
from drillion.block_ship_collision_handler import BlockShipCollisionHandler
from drillion.bullet_entity_creator import BulletEntityCreator
from drillion.cannon_entity_creator import CannonEntityCreator
from drillion.collision import CollisionDetector
from drillion.collision_dispatcher import CollisionDispatcher
from drillion.draw_phase import DrawPhase
from drillion.entity_manager import EntityManager
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

def main():
    pyglet.resource.path.append('../data')
    pyglet.resource.reindex()

    input_update_phase = UpdatePhase('input')
    control_update_phase = UpdatePhase('control')
    physics_update_phase = UpdatePhase('physics')
    collision_transform_update_phase = UpdatePhase('collision_transform')
    collision_update_phase = UpdatePhase('collision')
    animation_update_phase = UpdatePhase('animation')

    entity_manager = EntityManager()

    block_bullet_collision_handler = BlockBulletCollisionHandler(entity_manager)
    block_ship_collision_handler = BlockShipCollisionHandler(entity_manager)
    collision_handlers = {
        ('block', 'bullet'): block_bullet_collision_handler,
        ('block', 'ship'): block_ship_collision_handler,
    }
    collision_dispatcher = CollisionDispatcher(collision_handlers)

    collision_detector = CollisionDetector(listener=collision_dispatcher)
    collision_update_phase.add_handler(collision_detector)

    draw_phase = DrawPhase('draw')

    update_phases = [input_update_phase, control_update_phase,
                     physics_update_phase, collision_transform_update_phase,
                     collision_update_phase, animation_update_phase]
    draw_phases = [draw_phase]
    game = Game(update_phases, draw_phases)

    block_entity_creator = BlockEntityCreator(collision_detector, game.batch)
    bullet_entity_creator = \
        BulletEntityCreator(physics_update_phase,
                            collision_transform_update_phase,
                            animation_update_phase, draw_phase,
                            collision_detector, game.batch)
    ship_entity_creator = ShipEntityCreator(input_update_phase,
                                            control_update_phase,
                                            physics_update_phase,
                                            collision_transform_update_phase,
                                            animation_update_phase,
                                            draw_phase, game.key_state_handler,
                                            collision_detector, game.batch,
                                            bullet_entity_creator,
                                            entity_manager)
    cannon_entity_creator = CannonEntityCreator(animation_update_phase,
                                                draw_phase, game.batch)

    seed_x = random.random()
    seed_y = random.random()
    seed_z = random.random()

    noise_scale = 0.15

    for grid_x in xrange(-20, 20):
        for grid_y in xrange(-20, 20):
            if -2 <= grid_x < 2 and -1 <= grid_y < 1:
                continue
            noise_x = seed_x + noise_scale * float(grid_x)
            noise_y = seed_y + noise_scale * float(grid_y)
            noise_z = seed_z
            density = pnoise(noise_x, noise_y, noise_z)
            if density > 0.0:
                block_entity = block_entity_creator.create(grid_position=(grid_x, grid_y))
                entity_manager.add_entity(block_entity)

    ship_entity_1 = ship_entity_creator.create(position=(-2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               keys=PLAYER_1_SHIP_KEYS)
    entity_manager.add_entity(ship_entity_1)

    cannon_entity_1_1 = cannon_entity_creator.create(ship_entity_1,
                                                     position=(-0.5, 0.5),
                                                     angle=(0.0 * math.pi),
                                                     length=1.5, width=0.125)
    cannon_entity_1_2 = cannon_entity_creator.create(ship_entity_1,
                                                     position=(-0.5, 0.25),
                                                     angle=(0.0 * math.pi),
                                                     length=1.75, width=0.125)
    cannon_entity_1_3 = cannon_entity_creator.create(ship_entity_1,
                                                     position=(-0.5, -0.25),
                                                     angle=(0.0 * math.pi),
                                                     length=1.75, width=0.125)
    cannon_entity_1_4 = cannon_entity_creator.create(ship_entity_1,
                                                     position=(-0.5, -0.5),
                                                     angle=(0.0 * math.pi),
                                                     length=1.5, width=0.125)
    entity_manager.add_entity(cannon_entity_1_1)
    entity_manager.add_entity(cannon_entity_1_2)
    entity_manager.add_entity(cannon_entity_1_3)
    entity_manager.add_entity(cannon_entity_1_4)

    ship_entity_2 = ship_entity_creator.create(position=(2.0, 0.0),
                                               angle=(0.5 * math.pi),
                                               keys=PLAYER_2_SHIP_KEYS)
    entity_manager.add_entity(ship_entity_2)

    cannon_entity_2_1 = cannon_entity_creator.create(ship_entity_2,
                                                     position=(-0.5, 0.25),
                                                     angle=(0.0 * math.pi),
                                                     length=1.75, width=0.125)
    cannon_entity_2_2 = cannon_entity_creator.create(ship_entity_2,
                                                     position=(-0.5, 0.0),
                                                     angle=(0.0 * math.pi),
                                                     length=2.0, width=0.125)
    cannon_entity_2_3 = cannon_entity_creator.create(ship_entity_2,
                                                     position=(-0.5, -0.25),
                                                     angle=(0.0 * math.pi),
                                                     length=1.75, width=0.125)
    entity_manager.add_entity(cannon_entity_2_1)
    entity_manager.add_entity(cannon_entity_2_2)
    entity_manager.add_entity(cannon_entity_2_3)

    pyglet.clock.schedule(game.update)
    pyglet.app.run()

    update_phase_times = [(phase.total_time, phase.name)
                          for phase in update_phases]
    total_update_time = sum(time for time, name in update_phase_times)
    average_update_time = total_update_time / float(game.update_count)
    print 'Average update time: %f' % average_update_time
    for time, name in reversed(sorted(update_phase_times)):
        time_percentage = int(round(100.0 * time / total_update_time))
        print '%3d%%  %s' % (time_percentage, name)

    draw_phase_times = [(phase.total_time, phase.name)
                        for phase in draw_phases]
    total_draw_time = sum(time for time, name in draw_phase_times)
    average_draw_time = total_draw_time / float(game.draw_count)
    print 'Average draw time: %f' % average_draw_time

if __name__ == '__main__':
    main()
