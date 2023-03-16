from task_system_client.subscriber import create_subscriber
from cone.hooks.exception import setSysExceptHook


def start_task_system():
    def stop_subscriber(excType, excValue, tb):
        subscriber.stop()

    subscriber = create_subscriber()
    subscriber.start()

    setSysExceptHook(stop_subscriber)


if __name__ == '__main__':
    start_task_system()

