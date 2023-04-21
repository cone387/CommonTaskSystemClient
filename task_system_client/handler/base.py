

class BaseHandler:
    name = 'base_handler'

    def handle(self, e):
        raise NotImplementedError

    def __str__(self):
        return self.name
