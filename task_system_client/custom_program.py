import json
import locale
import os
import zipfile
import subprocess
import sys
import requests

SYS_ENCODING = locale.getpreferredencoding()


def run_in_subprocess(cmd, ret_logs=False):
    logs = []
    stdout = subprocess.PIPE if ret_logs else sys.stdout
    stderr = subprocess.PIPE if ret_logs else sys.stderr
    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    out, err = p.communicate()
    if out:
        logs.append(out.decode(SYS_ENCODING))
    if err:
        logs.append(err.decode(SYS_ENCODING))
    return not err, logs


class ProgramExecutor:

    def __new__(cls, path, file, args=None):
        if cls is ProgramExecutor:
            if not file:
                raise Exception('file is required')
            elif file.endswith('.py'):
                return PythonExecutor(file, args)
            elif file.endswith('.zip'):
                return ZipExecutor(file, args)
            elif file.endswith('.sh'):
                return ShellExecutor(file, args)
            raise Exception('Unsupported file type %s' % file)
        else:
            return super().__new__(cls)

    def __init__(self, path, file, args=None):
        self.working_path = path
        self.file = file
        if args:
            self.args = [x.strip() for x in args.split(' ')]
        else:
            self.args = []

    def prepare(self):
        pass

    def assert_runnable(self):
        pass

    def run(self, ret_logs=False):
        succeed, logs = run_in_subprocess(self.entrypoint, ret_logs)
        assert succeed, 'Failed to run %s, %s' % (self.file, '\n'.join(logs))
        return logs

    @property
    def entrypoint(self):
        raise NotImplementedError


def download_program(program_download_url, program_file):
    response = requests.get(program_download_url, stream=True)
    assert response.status_code == 200, 'Failed to download program: %s' % response.json()
    with open(program_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def start_custom_program(download_url=None, schedule: dict = None, ret_logs=False):
    if schedule is None:
        schedule = json.loads(sys.argv[2])
        download_url = sys.argv[1]
    program = schedule['task']['config']['custom_program']
    args = program.get('args')
    file = program.get('executable')
    # prepare program working path
    working_path = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(working_path):
        os.mkdir(working_path)

    # download program file
    program_file = os.path.join(working_path, os.path.basename(file.replace('\\', '/')))
    download_program(f"{download_url}{schedule['task']['id']}/", program_file)
    program = ProgramExecutor(working_path, program_file, args)
    program.prepare()
    program.assert_runnable()
    logs = program.run(ret_logs=ret_logs)
    if ret_logs:
        return logs
    sys.exit(0)


class PythonExecutor(ProgramExecutor):

    @property
    def entrypoint(self):
        return ' '.join(['python', self.file] + self.args)


class ZipExecutor(ProgramExecutor):

    def __init__(self, path, file, args=None):
        super().__init__(path, file, args)
        self.program = None

    def prepare(self):
        zip_file = zipfile.ZipFile(self.file)
        zip_file.extractall(self.working_path)
        zip_file.close()

        shell = os.path.join(self.working_path, 'main.sh')
        python = os.path.join(self.working_path, 'main.py')
        if os.path.exists(shell):
            self.program = ShellExecutor(self.working_path, shell, self.args)
        elif os.path.exists(python):
            self.program = PythonExecutor(self.working_path, python, self.args)

    def assert_runnable(self):
        assert self.program is not None, 'main.py or main.sh not found'

    @property
    def entrypoint(self):
        return self.program.entrypoint

    def run(self, ret_logs=False):
        self.program.assert_runnable()
        self.program.run(ret_logs=ret_logs)


class ShellExecutor(ProgramExecutor):

    def assert_runnable(self):
        assert sys.platform == 'win32', 'shell is not supported in windows'

    @property
    def entrypoint(self):
        return ' '.join(['sh', self.file] + self.args)
