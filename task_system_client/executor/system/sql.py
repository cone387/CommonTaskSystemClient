from task_system_client.executor import Executor
from task_system_client.executor.system import SystemExecutor
from task_system_client.executor.base import NoRetryException
import pymysql


@Executor()
class SqlExecutor(SystemExecutor):
    parent = 'SQL执行'

    def run(self):
        result = []
        commands = self.schedule.task.config.get('script', '').split(';')
        sql_config = self.schedule.task.config.get('sql_config') or {}
        required_fields = ['host', 'user', 'password', 'db']
        for field in required_fields:
            if field not in sql_config:
                raise NoRetryException(f'config {field} is required')
        connection = pymysql.connect(**sql_config)
        with connection.cursor() as cursor:
            for sql in commands:
                sql = sql.strip()
                if sql:
                    if sql.lower().startswith('select'):
                        cursor.execute(sql)
                        cmd_result = {
                            'script': sql,
                            'result': cursor.fetchall()
                        }
                    else:
                        cmd_result = {
                            'script': sql,
                            'result': cursor.execute(sql)
                        }
                    result.append(cmd_result)
        return result
