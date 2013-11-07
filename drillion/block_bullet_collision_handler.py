from drillion.collision_handler import CollisionHandler

class BlockBulletCollisionHandler(CollisionHandler):
    def __init__(self, entity_manager):
        self._entity_manager = entity_manager

    def on_collision_add(self, collision):
        block_category, block_entity = collision.body_a.user_data
        bullet_category, bullet_entity = collision.body_b.user_data
        self._entity_manager.remove_entity(block_entity)
        self._entity_manager.remove_entity(bullet_entity)
