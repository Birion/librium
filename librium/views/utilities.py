import json

import marshmallow as ma
from webargs.fields import DelimitedList


class MyBoolean(ma.fields.Boolean):
    truthy = ma.fields.Boolean.truthy.union({"on"})
    falsy = ma.fields.Boolean.falsy.union({"off"})


class SeriesSchema(ma.Schema):
    series = ma.fields.Integer(required=True)
    idx = ma.fields.Float(missing=0.0)

    @ma.pre_load
    def clean(self, data, **kwargs):
        data = dict(data)
        if data["idx"] == "":
            data["idx"] = 0.0
        return data

    class Meta:
        unknown = ma.INCLUDE


class BookSchema(ma.Schema):
    title = ma.fields.String()
    isbn = ma.fields.String()
    format = ma.fields.Integer()
    released = ma.fields.Integer()
    price = ma.fields.Float()
    page_count = ma.fields.Integer()
    read = MyBoolean(missing=False)
    authors = DelimitedList(ma.fields.Integer())
    genres = ma.fields.List(ma.fields.Integer())
    publishers = ma.fields.List(ma.fields.Integer())
    languages = ma.fields.List(ma.fields.Integer())
    series = ma.fields.Nested(SeriesSchema, many=True)

    @ma.pre_load
    def parse_series(self, data, **kwargs):
        data = dict(data)
        if "series" in data.keys():
            data["series"] = json.loads(data.get("series"))
        return data

    @ma.pre_load
    def parse_isbn(self, data, **kwargs):
        data = dict(data)
        if "isbn" in data.keys():
            data["isbn"] = data["isbn"].replace("-", "")
        return data

    class Meta:
        unknown = ma.EXCLUDE
