from .dispatcher import Dispatcher, DispatchError
from ...utils.class_loader import load_class


def get_dispatcher_cls(dispatch=None):
    return load_class(dispatch, Dispatcher)


def create_dispatcher(dispatch=None) -> Dispatcher:
    return get_dispatcher_cls(dispatch)()
