from drillion.collision_handler import CollisionHandler
from drillion.health_component import HealthComponent

class BlockBulletCollisionHandler(CollisionHandler):
    def __init__(self, entity_manager):
        self._entity_manager = entity_manager

    def on_collision_add(self, collision):
        block_category, block_entity = collision.body_a.user_data
        bullet_category, bullet_entity = collision.body_b.user_data
        block_health_component = block_entity.find_component(HealthComponent)
        block_health_component.health -= 0.1
        if block_health_component.at_min_health:
            self._entity_manager.remove_entity(block_entity)
        self._entity_manager.remove_entity(bullet_entity)
