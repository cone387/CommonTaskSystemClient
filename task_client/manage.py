from task_client.subscriber import SubscriberPool


def main():
    subscriber = SubscriberPool()
    subscriber.start()


if __name__ == '__main__':
    main()

