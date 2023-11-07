import os
import socket
import requests
from task_system_client.executor import Executor
from task_system_client.executor.system import SystemExecutor
from task_system_client.settings import (
    logger, CLIENT_REGISTER_URL, GROUP, CLIENT_ID,
    CONSUME_QUEUE_NAME, CLIENT_SIGNAL_URL, CLIENT_ACTION_URL, SUBSCRIPTION_URL)


is_in_docker = os.path.exists('/.dockerenv')


def get_container_info():
    import docker.errors
    if is_in_docker:
        short_id = socket.gethostname()
        try:
            container = docker.from_env().containers.get(short_id)
            return {
                'id': short_id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else '',
                'command': container.attrs['Config']['Cmd'],
                'ip': container.attrs['NetworkSettings']['IPAddress'],
            }
        except (docker.errors.NotFound, docker.errors.DockerException):
            return None
    else:
        return None


def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def get_hostname():
    return socket.gethostname()


def register_client():
    data = {
        'machine': {
            'mac': get_mac_address(),
            'hostname': socket.gethostname(),
            'intranet_ip': socket.gethostbyname(socket.gethostname()),
            'group': GROUP,
        },
        'id': CLIENT_ID,
        'queue': CONSUME_QUEUE_NAME,
        'consume_url': SUBSCRIPTION_URL,
        'container': get_container_info(),
        'process_id': os.getpid(),
    }
    try:
        response = requests.post(CLIENT_REGISTER_URL, json=data)
        if response.status_code == 200:
            logger.info("register succeed: %s", response.json())
        else:
            raise Exception(response.json())
    except Exception as e:
        logger.exception(e)


def stop_client():
    try:
        response = requests.post(f"{CLIENT_ACTION_URL}stop/", params={'id': CLIENT_ID, 'queue': CONSUME_QUEUE_NAME})
        if response.status_code == 200:
            logger.info("stop succeed: %s", response.json())
        else:
            raise Exception(response.json())
        os._exit(0)
    except Exception as e:
        logger.exception(e)


def read_log():
    if is_in_docker:
        import docker.errors
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(socket.gethostname())
            logs = container.logs(tail=1000)
        except (docker.errors.NotFound, docker.errors.DockerException):
            return "can't find container"
        return logs.decode('utf-8')
    else:
        return "client is not running in docker, can't read log"


def send_log():
    try:
        response = requests.post(f"{CLIENT_ACTION_URL}log/", params={'id': CLIENT_ID, 'queue': CONSUME_QUEUE_NAME},
                                 data={'log': read_log()})
        if response.status_code == 200:
            logger.info("log succeed: %s", response.json())
        else:
            raise Exception(response.json())
    except Exception as e:
        logger.exception(e)


@Executor()
class SignalExecutor(SystemExecutor):
    name = '系统信号'

    def run(self):
        signal = self.schedule.task.config.get('signal', 'register')
        if signal == 'register':
            register_client()
        elif signal == 'stop':
            stop_client()
        elif signal == 'log':
            send_log()
        else:
            raise Exception(f'unknown signal: {signal}')
