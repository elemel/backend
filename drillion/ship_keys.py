from pyglet.window import key

PLAYER_SHIP_KEYS = dict(left=[key.A, key.J], right=[key.D, key.L],
                        thrust=[key.W, key.I], fire=[key.S, key.K])
PLAYER_1_SHIP_KEYS = dict(left=[key.A], right=[key.D], thrust=[key.W],
                          fire=[key.S])
PLAYER_2_SHIP_KEYS = dict(left=[key.J], right=[key.L], thrust=[key.I],
                          fire=[key.K])
