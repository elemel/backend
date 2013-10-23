from drillion.component import Component

class CollisionComponent(Component):
    def __init__(self, transform_component, update_phase, body, detector):
        self.transform_component = transform_component
        self.update_phase = update_phase
        self.body = body
        self.detector = detector

    def create(self):
        if self.update_phase is not None:
            self.update_phase.add_handler(self)
        self.detector.add_body(self.body)

    def delete(self):
        self.detector.remove_body(self.body)
        if self.update_phase is not None:
            self.update_phase.remove_handler(self)

    def update(self, dt):
        self.body.transform.assign(*self.transform_component.transform)
        self.body.touch()
