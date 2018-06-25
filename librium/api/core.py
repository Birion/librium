from pprint import pprint

import attr
from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound
from flask import abort

from librium.database import (
    db_session,
    Author,
    Format,
    Genre,
    Language,
    Publisher,
    Series,
    SeriesIndex,
    Book,
)


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
        "format": Format,
    }

    def __attrs_post_init__(self):
        super(BookAPI, self).__init__(self.table)

    def create_one(self, _book):
        try:
            series = []
            for _series in _book["series"]:
                idx = _series.get("idx", 0)
                name = _series.get("name")
                series_details = self.add(self.LOOKUP["series"], {"name": name})
                series.append(SeriesIndex(**{"idx": idx, "series": series_details}))
            pprint(series)
            del _book["series"]
        except KeyError:
            pass

        for key in _book:
            if key in self.LOOKUP.keys():
                if isinstance(_book[key], list):
                    for idx, item in enumerate(_book[key]):
                        _book[key][idx] = self.add(self.LOOKUP[key], item)
                else:
                    _book[key] = self.add(self.LOOKUP[key], _book[key])

        book = self.table(**_book)
        try:
            book.series = series
        except UnboundLocalError:
            pass
        book.make_uuid()
        return book

    def create(self, **kwargs):
        book = self.create_one(kwargs["book"])
        if book._id:
            return abort(400)
        db_session.add(book)
        db_session.commit()

    def create_many(self, **kwargs):
        for _book in kwargs["books"]:
            book = self.create_one(_book)
            if book._id:
                return abort(400)
            db_session.add(book)
            db_session.commit()

    def update(self, **kwargs):
        pass

    @staticmethod
    def add(table, item):
        try:
            _item = table.query.filter_by(**item).one()
        except NoResultFound:
            _item = table(**item)
            try:
                _item.make_uuid()
            except AttributeError:
                pass
        return _item
