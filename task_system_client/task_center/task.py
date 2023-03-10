
class Category:
    def __init__(self, category):
        self.name = category['name']
        self.parent = Category(category['parent']) if category.get('parent') else None


class Task:

    def __init__(self, task):
        self.id = task['id']
        self.name = task['name']
        self.category = Category(task['category'])
        self.config = task.get('config', {}) or {}
        self.parent = Task(task['parent']) if task.get('parent') else None

        parent = self.parent
        names = [self.name]
        while parent:
            names.append(parent.name)
            parent = parent.parent
        self.unique_name = '-'.join(reversed(names))

        names = [self.category.name]
        parent = self.category.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        self.unique_category = '-'.join(reversed(names))

    def __str__(self):
        return 'Task(id=%s, name=%s)' % (self.id, self.unique_name)


class TaskSchedule:

    def __init__(self, schedule):
        self.schedule_id = schedule['id']
        self.schedule_time = schedule['schedule_time']
        self.callback = schedule['callback']
        self.task = Task(schedule['task'])

    def __str__(self):
        return 'TaskSchedule(id=%s, time=%s, task=%s)' % (
            self.schedule_id, self.schedule_time, self.task
        )
