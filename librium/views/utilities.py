import simplejson as json

from marshmallow import pre_load, EXCLUDE, Schema, fields, INCLUDE
from webargs.fields import DelimitedList


class MyBoolean(fields.Boolean):
    truthy = fields.Boolean.truthy.union({"on"})
    falsy = fields.Boolean.falsy.union({"off"})


class SeriesSchema(Schema):
    series = fields.Integer(required=True)
    idx = fields.Float(load_default=0.0)

    @pre_load
    def clean(self, data, **kwargs):
        data = dict(data)
        if data["idx"] == "":
            data["idx"] = 0.0
        return data

    class Meta:
        unknown = INCLUDE


class BookSchema(Schema):
    title = fields.String()
    isbn = fields.String()
    format = fields.Integer()
    released = fields.Integer()
    price = fields.Float()
    page_count = fields.Integer()
    read = MyBoolean(load_default=False)
    authors = DelimitedList(fields.Integer())
    genres = DelimitedList(fields.Integer())
    publishers = DelimitedList(fields.Integer())
    languages = DelimitedList(fields.Integer())
    series = fields.Nested(SeriesSchema, many=True)

    @pre_load
    def parse_series(self, data, **kwargs):
        data = dict(data)
        if "series" in data.keys():
            data["series"] = json.loads(data.get("series"))
        return data

    @pre_load
    def parse_isbn(self, data, **kwargs):
        data = dict(data)
        if "isbn" in data.keys():
            data["isbn"] = data["isbn"].replace("-", "")
        return data

    class Meta:
        unknown = EXCLUDE
