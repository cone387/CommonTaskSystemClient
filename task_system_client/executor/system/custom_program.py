import docker
import json
from task_system_client.executor.base import NoRetryException
from task_system_client.executor import Executor
from task_system_client.executor.system import SystemExecutor
from task_system_client.settings import PROGRAM_DOWNLOAD_URL
from task_system_client.custom_program import start_custom_program


class Container:

    def __init__(self, schedule, image):
        self.schedule = schedule
        self.image = image
        self.working_path = '/home/admin'

    def run(self):
        client = docker.from_env()
        # auto_remove similar to --rm
        # detach similar to -d, so detach and auto_remove can't be True at the same time
        return client.containers.run(
            self.image,
            command="cts-execute %s '%s'" % (PROGRAM_DOWNLOAD_URL, json.dumps(self.schedule.content)),
            # auto_remove=True,
            remove=True,
            working_dir=self.working_path,
            detach=False
        ).decode()


@Executor()
class CustomProgramExecutor(SystemExecutor):
    parent = '自定义程序'

    def run(self):
        custom_program = self.schedule.task.config['custom_program']
        docker_image = custom_program.get('docker_image') or 'cone387/common-task-system-client:latest'
        run_in_container = custom_program.get('run_in_container', True)
        try:
            if run_in_container:
                container = Container(self.schedule, image=docker_image)
                logs = container.run()
            else:
                logs = start_custom_program(PROGRAM_DOWNLOAD_URL, self.schedule.content, ret_logs=True)
        except Exception as e:
            raise NoRetryException('Failed to run program: %s' % e)
        return logs
