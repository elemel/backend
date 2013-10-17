from bromine.component import Component
from bromine.maths import Transform2

class AnimationComponent(Component):
    def __init__(self, transform_component, sprite_component, update_phase,
                 draw_phase):
        super(AnimationComponent, self).__init__()
        self.transform_component = transform_component
        self.sprite_component = sprite_component
        self.update_phase = update_phase
        self.draw_phase = draw_phase
        self.old_transform = Transform2()
        self.transform = Transform2()
        self.mixed_transform = Transform2()

    def create(self):
        self.transform.assign(*self.transform_component.transform)
        self.old_transform.assign(*self.transform)
        self.update_phase.add_handler(self)
        self.draw_phase.add_handler(self)

    def delete(self):
        self.draw_phase.remove_handler(self)
        self.update_phase.remove_handler(self)

    def update(self, dt):
        self.old_transform.assign(*self.transform)
        self.transform.assign(*self.transform_component.transform)

    def draw(self, alpha):
        self.mixed_transform.mix(self.old_transform, self.transform, alpha)
        self.sprite_component.sprite.transform = self.mixed_transform
