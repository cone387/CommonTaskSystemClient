from task_client.subscriber import SubscriberPool
from cone.hooks.exception import setSysExceptHook
from task_client.settings import SUBSCRIBER_NUM


def main():
    def stop_subscriber(excType, excValue, tb):
        subscriber.stop()

    subscriber = SubscriberPool(num=SUBSCRIBER_NUM)
    subscriber.start()

    setSysExceptHook(stop_subscriber)


if __name__ == '__main__':
    main()

