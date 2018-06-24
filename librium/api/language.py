from librium.database import Language
from .util import get_all, add_one


def create(**kwargs):
    add_one(Language, **kwargs)


def read(**kwargs):
    return get_all(Publisher, **kwargs)


def read_one():
    pass


def update():
    pass


def delete():
    pass
