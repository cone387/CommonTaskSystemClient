from datetime import datetime


class Category:
    def __init__(self, category):
        if category is None:
            self.name = None
            self.parent = None
            self.config = {}
        else:
            self.name = category['name']
            self.parent = Category(category['parent'])
            self.config = category.get('config') or {}

    def __bool__(self):
        return bool(self.name)


class Task:

    def __init__(self, task):
        self.id = task['id']
        self.name = task['name']
        self.category = Category(task['category'])
        self.config = task.get('config') or {}
        self.parent = Task(task['parent']) if task.get('parent') else None
        self.content = task

        parent = self.parent
        names = [self.name]
        while parent:
            names.append(parent.name)
            parent = parent.parent
        self.unique_name = '-'.join(reversed(names))

        if self.category:
            names = [self.category.name]
            parent = self.category.parent
            while parent:
                names.append(parent.name)
                parent = parent.parent
            self.unique_category = '-'.join(reversed(names))
        else:
            self.unique_category = None

    def __str__(self):
        return 'Task(id=%s, name=%s)' % (self.id, self.unique_name)

    __repr__ = __str__


class TaskSchedule:

    def __init__(self, schedule):
        self.schedule_id = schedule['id']
        self.schedule_time = datetime.strptime(schedule['schedule_time'], '%Y-%m-%d %H:%M:%S')
        self.callback = schedule['callback']
        self.task = Task(schedule['task'])
        self.config = schedule.get('config') or {}

    def __str__(self):
        return 'TaskSchedule(id=%s, time=%s, task=%s)' % (
            self.schedule_id, self.schedule_time, self.task
        )

    __repr__ = __str__

    def __hash__(self):
        return hash("%s-%s" % (self.schedule_id, self.schedule_time))
