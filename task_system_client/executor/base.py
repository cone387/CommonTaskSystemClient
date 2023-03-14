from cone.utils.classes import ClassManager


CategoryNameExecutor = ClassManager(name='CategoryNameExecutor', unique_keys=['category', 'name'])

NameExecutor = ClassManager(name='NameExecutor', unique_keys=['name'])
