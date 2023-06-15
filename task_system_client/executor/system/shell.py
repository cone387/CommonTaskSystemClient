import sys
import subprocess
from task_system_client.executor import BaseExecutor, Executor


@Executor()
class ShellExecutor(BaseExecutor):
    name = 'Shell执行'

    def run(self):
        if sys.platform == 'win32':
            raise RuntimeError('Windows系统不支持shell命令执行')

        commands = self.schedule.task.config.get('script', '').split(';')
        filename = '/tmp/shell_executor.sh'
        with open(filename, 'w') as f:
            f.write('#!/bin/bash -e \n')
            f.write('; \n'.join(commands))
        p = subprocess.Popen(f'/bin/bash {filename}', shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            raise RuntimeError(err)
        return out.decode('utf-8')
