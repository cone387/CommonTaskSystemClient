import importlib


def load_class(obj=None, default=None) -> type:
    if obj is None:
        obj = default
    elif isinstance(obj, str):
        module, cls = obj.rsplit('.', 1)
        obj = getattr(importlib.import_module(module), cls)
    elif type(obj) is type and issubclass(obj, default):
        pass
    else:
        raise TypeError("dispatch must be a str or a subclass of Dispatcher")
    return obj
