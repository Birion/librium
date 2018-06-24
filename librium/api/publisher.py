from librium.database import Publisher
from .util import get_all, add_one, get_one, change_one


def create(**kwargs):
    return add_one(Publisher, **kwargs)


def read(**kwargs):
    return get_all(Publisher, **kwargs)


def read_one(**kwargs):
    return get_one(Publisher, **kwargs)


def update(**kwargs):
    change_one(Publisher, **kwargs)


def delete(**kwargs):
    pass
