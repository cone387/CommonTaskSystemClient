import os
from task_system_client.client import create_client
from task_system_client.settings import args
from cone.hooks.exception import setSysExceptHook


def start_task_system():
    if args.path:
        """
            从指定目录中加载Executor
        """
        import sys
        import shutil
        from task_system_client.executor import Executor
        if sys.platform == 'win32':
            tmp_path = os.path.join(os.environ['USERPROFILE'], '.task-system-client')
        else:
            tmp_path = os.path.join('/tmp/', 'task-system-client')
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)

        executor_path = os.path.join(tmp_path, 'tmp_executors')
        os.mkdir(executor_path)
        sys.path.append(tmp_path)

        for path in args.path.split(','):
            path = path.strip()
            assert os.path.exists(path), f'{path} not exists'
            path_name = os.path.basename(path)
            shutil.copy(path, os.path.join(executor_path, path_name))
            Executor.register_from('tmp_executors.%s' % path_name)

    def stop_client(excType, excValue, tb):
        subscriber.stop()

    subscriber = create_client()
    subscriber.start()

    setSysExceptHook(stop_client)


if __name__ == '__main__':
    start_task_system()
