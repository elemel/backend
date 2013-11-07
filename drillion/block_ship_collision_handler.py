from drillion.collision_handler import CollisionHandler

class BlockShipCollisionHandler(CollisionHandler):
    def __init__(self, entity_manager):
        self._entity_manager = entity_manager

    def on_collision_add(self, collision):
        ship_category, ship_entity = collision.body_b.user_data
        self._entity_manager.remove_entity(ship_entity)
