from pyglet.window import key

PLAYER_SHIP_KEYS = dict(left=[key.A, key.LEFT], right=[key.D, key.RIGHT],
                        thrust=[key.W, key.UP], fire=[key.S, key.DOWN])
PLAYER_1_SHIP_KEYS = dict(left=[key.A], right=[key.D], thrust=[key.W],
                          fire=[key.S])
PLAYER_2_SHIP_KEYS = dict(left=[key.LEFT], right=[key.RIGHT],
                          thrust=[key.UP], fire=[key.DOWN])
