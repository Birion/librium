from librium.database import Publisher
from .util import get_all, add_one


def create(**kwargs):
    add_one(Publisher, **kwargs)


def read(**kwargs):
    return get_all(Publisher, **kwargs)


def read_one():
    pass


def update():
    pass


def delete():
    pass