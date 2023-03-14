from task_system_client.subscriber import SubscriberPool
from cone.hooks.exception import setSysExceptHook
from task_system_client.settings import SUBSCRIBER_NUM


def start_task_system():
    def stop_subscriber(excType, excValue, tb):
        subscriber.stop()

    subscriber = SubscriberPool(num=SUBSCRIBER_NUM)
    subscriber.start()

    setSysExceptHook(stop_subscriber)


if __name__ == '__main__':
    start_task_system()

