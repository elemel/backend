from backend.component import Component
from backend.ship_keys import PLAYER_SHIP_KEYS

class ShipInputComponent(Component):
    def __init__(self, update_phase, control_component, key_state_handler,
                 keys=PLAYER_SHIP_KEYS):
        super(ShipInputComponent, self).__init__()

        self._update_phase = update_phase
        self._control_component = control_component
        self._key_state_handler = key_state_handler

        self._left_keys = list(keys['left'])
        self._right_keys = list(keys['right'])
        self._thrust_keys = list(keys['thrust'])
        self._fire_keys = list(keys['fire'])

    def create(self):
        self._update_phase.add_handler(self)

    def delete(self):
        self._update_phase.remove_handler(self)

    def update(self, dt):
        left_control = self.get_control(self._left_keys)
        right_control = self.get_control(self._right_keys)
        thrust_control = self.get_control(self._thrust_keys)
        fire_control = self.get_control(self._fire_keys)

        turn_control = left_control - right_control

        self._control_component.turn_control = turn_control
        self._control_component.thrust_control = thrust_control

    def get_control(self, keys):
        for key in keys:
            if self._key_state_handler[key]:
                return 1.0
        return 0.0
