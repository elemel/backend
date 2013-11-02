from pyglet.window import key

PLAYER_1_SHIP_KEYS = dict(left=[key.A], right=[key.D],
                          thrust=[key.S, key.LSHIFT], fire=[key.W, key.SPACE])
PLAYER_2_SHIP_KEYS = dict(left=[key.J], right=[key.L], thrust=[key.K],
                          fire=[key.I])
