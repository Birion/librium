import json

from sqlalchemy import desc, asc
from flask import abort, Response

from librium.database import db_session


def get_all(table, **kwargs):
    offset = kwargs["offset"]
    length = kwargs["offset"] + kwargs["length"]
    column = kwargs["sort"]
    f = asc if kwargs["asc"] else desc
    return table.query.order_by(f(column))[offset:length]


def add_one(table, **kwargs):
    if table.query.filter_by(**kwargs).one_or_none():
        return abort(400)
    obj = table(**kwargs)
    db_session.add(obj)
    db_session.commit()


def get_one(table, **kwargs):
    obj = table.query.filter_by(**kwargs).one_or_none()
    if not obj:
        return abort(404)
    return obj


def change_one(table, **kwargs):
    obj = table.query.filter_by(id=kwargs["id"]).one_or_none()
    if not obj:
        return abort(404)
    obj.name = kwargs["name"]
    db_session.commit()
