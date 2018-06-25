from pprint import pprint

import attr
from sqlalchemy import desc, asc
from flask import abort

from librium.database import db_session, Author, Format, Genre, Language, Publisher, Series, Book


@attr.s
class API:
    table = attr.ib()

    def create(self, **kwargs):
        if self.table.query.filter_by(**kwargs).one_or_none():
            return abort(400)
        obj = self.table(**kwargs)
        db_session.add(obj)
        db_session.commit()

    def read(self, **kwargs):
        offset = kwargs["offset"]
        length = kwargs["offset"] + kwargs["length"]
        column = kwargs["sort"]
        f = asc if kwargs["asc"] else desc
        return self.table.query.order_by(f(column))[offset:length]

    def read_one(self, **kwargs):
        obj = self.table.query.filter_by(**kwargs).one_or_none()
        if not obj:
            return abort(404)
        return obj

    def update(self, **kwargs):
        obj = self.table.query.filter_by(_id=kwargs["_id"]).one_or_none()
        if not obj:
            return abort(404)
        obj.name = kwargs["name"]
        db_session.commit()

    def delete(self, **kwargs):
        obj = self.table.query.filter_by(_id=kwargs["_id"]).one_or_none()
        if not obj:
            return abort(404)
        db_session.delete(obj)
        db_session.commit()


@attr.s
class BookAPI(API):
    table = attr.ib(default=Book)
    LOOKUP = {
        "authors": Author,
        "genres": Genre,
        "formats": Format,
        "languages": Language,
        "publishers": Publisher,
        "series": Series,
        "format": Format
    }

    def __attrs_post_init__(self):
        super(BookAPI, self).__init__(self.table)

    def create(self, **kwargs):
        _book = kwargs["book"]
        book = self.table()
        for key in _book:
            if key in self.LOOKUP.keys():
                if key == "series":
                    for idx, item in enumerate(_book[key]):
                        series = self.add(Series, item["series"])
                        _book[key][idx]["series"] = series
                elif isinstance(_book[key], list):
                    for idx, item in enumerate(_book[key]):
                        _book[key][idx] = self.add(self.LOOKUP[key], item)
                else:
                    _book[key] = self.add(self.LOOKUP[key], _book[key])
        pprint(_book)

        pprint(self.table(**_book))

    def update(self, **kwargs):
        pass

    @staticmethod
    def add(table, item):
        _item = table.query.filter_by(**item).one_or_none()
        if not _item:
            _item = table(**item)
        return _item

    @staticmethod
    def remove(table, item):
        _item = table.query.filter_by(**item).one_or_none()
        return _item
