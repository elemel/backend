from drillion.component import Component
from drillion.maths import clamp

class HealthComponent(Component):
    def __init__(self, update_phase, health=1.0, min_health=0.0,
                 max_health=1.0, regeneration=0.0, epsilon=0.001):
        self._update_phase = update_phase
        self._health = health
        self._min_health = min_health
        self._max_health = max_health
        self._regeneration = regeneration
        self._epsilon = epsilon
        self._active = False
        self._healing = False

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, health):
        self._health = health
        self._update_healing()

    @property
    def min_health(self):
        return self._min_health

    @min_health.setter
    def min_health(self, min_health):
        self._min_health = min_health
        self._update_healing()

    @property
    def max_health(self):
        return self._max_health

    @max_health.setter
    def max_health(self, max_health):
        self._max_health = max_health
        self._update_healing()

    @property
    def regeneration(self):
        return self._regeneration

    @regeneration.setter
    def regeneration(self, regeneration):
        self._regeneration = regeneration
        self._update_healing()

    @property
    def epsilon(self):
        return self._epsilon

    @epsilon.setter
    def epsilon(self, epsilon):
        self._epsilon = epsilon
        self._update_healing()

    @property
    def at_min_health(self):
        return self._health < self._min_health + self._epsilon

    @property
    def at_max_health(self):
        return self._health > self._max_health - self._epsilon

    def create(self):
        self._active = True
        self._update_healing()

    def delete(self):
        self._active = False
        self._update_healing()

    def update(self, dt):
        self._health = clamp(self._health + dt * self._regeneration,
                             self._min_health, self._max_health)
        self._update_healing()

    def _update_healing(self):
        healing = self._is_healing()

        if healing != self._healing:
            if self._healing:
                self._update_phase.remove_handler(self)
            self._healing = healing
            if self._healing:
                self._update_phase.add_handler(self)

    def _is_healing(self):
        if not self._active:
            return False
        if self._regeneration > self._epsilon:
            return not self.at_max_health
        if self._regeneration < -self._epsilon:
            return not self.at_min_health
        return False
