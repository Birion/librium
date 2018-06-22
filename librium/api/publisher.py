from librium.database import Publisher
from .util import get_all


def create():
    pass


def read(**kwargs):
    publisher = get_all(Publisher, **kwargs)
    return publisher


def read_one():
    pass


def update():
    pass


def delete():
    pass
