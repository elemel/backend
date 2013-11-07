from drillion.collision import CollisionListener

class CollisionDispatcher(CollisionListener):
    def __init__(self, handlers={}):
        self._handlers = dict(handlers)

    def on_collision_add(self, collision):
        key = self._get_key(collision)
        handler = self._handlers.get(key)
        if handler is not None:
            handler.on_collision_add(collision)

    def on_collision_remove(self, collision):
        key = self._get_key(collision)
        handler = self._handlers.get(key)
        if handler is not None:
            handler.on_collision_remove(collision)

    def _get_key(self, collision):
        category_a, entity_a = collision.body_a.user_data
        category_b, entity_b = collision.body_b.user_data
        if entity_a.key == -1 or entity_b.key == -1:
            return None
        else:
            return category_a, category_b
