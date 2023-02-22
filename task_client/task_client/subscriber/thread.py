from threading import Thread, Event
from ..task_center.subscription import get_subscription_cls, create_subscription
from ..task_center.dispatch import get_dispatcher_cls, create_dispatcher, DispatchError
from ..settings import SUBSCRIPTION, DISPATCHER
import time


class ThreadSubscriber(Thread):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, name='Subscribe'):
        super().__init__(name=name, daemon=True)
        self._state = Event()
        self._state.set()
        self.start_time = time.time()
        self.dispatcher = create_dispatcher(self.DISPATCHER or DISPATCHER)
        self.subscription = create_subscription(self.SUBSCRIPTION or SUBSCRIPTION)

    def run(self):
        subscription = self.subscription
        dispatcher = self.dispatcher
        while self._state.is_set():
            self._state.wait()
            # try:
            task = subscription.get()
            executor = dispatcher.dispatch(task)
            executor.process()
            # except Exception as e:
            #     print("Subscriber error: %s" % e)
            time.sleep(1)

    def stop(self):
        self._state.clear()
