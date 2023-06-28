from .dispatcher import (
    Dispatcher, NameDispatcher, CategoryAndNameDispatcher,
    CategoryParentNameDispatcher, FullCategoryAndNameDispatcher,
    ParentAndOptionalNameDispatcher,
    CategoryParentAndOptionalNameDispatcher
)
from task_system_client.utils.class_loader import load_class


def get_dispatcher_cls(dispatch=None):
    return load_class(dispatch, CategoryParentAndOptionalNameDispatcher)


def create_dispatcher(dispatch=None) -> Dispatcher:
    return get_dispatcher_cls(dispatch)()
