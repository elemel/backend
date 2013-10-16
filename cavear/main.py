from cavear.boulder_entity_creator import BoulderEntityCreator
from cavear.color import CYAN, WHITE, YELLOW
from cavear.draw_phase import DrawPhase
from cavear.game import Game
from cavear.ship_keys import PLAYER_1_SHIP_KEYS, PLAYER_2_SHIP_KEYS
from cavear.ship_entity_creator import ShipEntityCreator
from cavear.update_phase import UpdatePhase

import pyglet
from pyglet.window import key
from pyglet.gl import *
import math

def main():
    pyglet.resource.path.append('../data')
    pyglet.resource.reindex()

    input_update_phase = UpdatePhase()
    control_update_phase = UpdatePhase()
    physics_update_phase = UpdatePhase()
    animation_update_phase = UpdatePhase()

    draw_phase = DrawPhase()

    update_phases = [input_update_phase, control_update_phase,
                     physics_update_phase, animation_update_phase]
    draw_phases = [draw_phase]
    game = Game(update_phases, draw_phases)

    ship_entity_creator = ShipEntityCreator(input_update_phase,
                                            control_update_phase,
                                            physics_update_phase,
                                            animation_update_phase,
                                            draw_phase, game.key_state_handler)
    boulder_entity_creator = BoulderEntityCreator()

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

    boulder_entity = boulder_entity_creator.create(position=(0.0, 2.0))
    game.add_entity(boulder_entity)

    pyglet.clock.schedule(game.update)
    pyglet.app.run()

if __name__ == '__main__':
    main()
