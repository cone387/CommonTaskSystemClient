

SUBSCRIPTION_ENGINE = {
    "HttpSubscription": {
        # "subscription_url": "https://api.cone387.top/t/queue/next/",
        # "subscription_url": "http://127.0.0.1:8000/t/schedule/queue/get/",
        "subscription_url": "http://127.0.0.1:8000/t/schedule/queue/7/",
    }
}


DISPATCHER = "task_client.task_center.dispatch.Dispatcher"
SUBSCRIPTION = "task_client.task_center.subscription.HttpSubscription"
SUBSCRIBER = "task_client.subscriber.ThreadSubscriber"
