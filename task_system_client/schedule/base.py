from datetime import datetime


class Category:
    def __init__(self, category):
        self.name = category['name']
        self.parent = Category(category['parent']) if category.get('parent') else None
        self.config = category.get('config') or {}


class Task:

    def __init__(self, task):
        self.id = task['id']
        self.name = task['name']
        self.category = Category(task['category']) if task.get('category') else None
        self.config = task.get('config') or {}
        self.parent = Task(task['parent']) if task.get('parent') else None
        self.content = task

    def __str__(self):
        return 'Task(id=%s, name=%s)' % (self.id, self.name)

    __repr__ = __str__


class Schedule:

    def __init__(self, schedule):
        self.id = schedule['id']
        self.schedule_time = datetime.strptime(schedule['schedule_time'], '%Y-%m-%d %H:%M:%S')
        self.callback = schedule['callback']
        self.task = Task(schedule['task'])
        self.queue = schedule.get('queue', None)
        self.config = schedule.get('config') or {}
        self.generator = schedule.get('generator', None)
        self.last_log = schedule.get('last_log', None)
        self.preserve_log = schedule.get('preserve_log', True)
        self.content = schedule

    def __str__(self):
        return 'Schedule(id=%s, time=%s, task=%s)' % (
            self.id, self.schedule_time, self.task
        )

    __repr__ = __str__

    def __hash__(self):
        return hash("%s-%s" % (self.id, self.schedule_time))
