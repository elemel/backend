class EntityManager(object):
    def __init__(self):
        self._entities = {}
        self._next_key = 0

    def add_entity(self, entity):
        entity.key = self._generate_key()
        self._entities[entity.key] = entity
        entity.create()

    def remove_entity(self, entity):
        for child in reversed(list(entity.children)):
            self.remove_entity(child)
        entity.delete()
        del self._entities[entity.key]
        entity.key = -1

    def _generate_key(self):
        key = self._next_key
        self._next_key += 1
        return key
