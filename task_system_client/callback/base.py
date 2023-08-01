from cone.utils.classes import ClassManager

Callback = ClassManager(name='CallbackManager', unique_keys=['name'])


class BaseCallback:
    name = None

    def __init__(self, config=None, executor=None):
        self.config = config
        self.executor = executor

    def run(self):
        pass

    def start(self):
        self.run()
