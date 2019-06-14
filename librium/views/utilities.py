import json

from marshmallow import Schema, fields, pre_load


class MyBoolean(fields.Boolean):
    truthy = fields.Boolean.truthy.union({"on"})
    falsy = fields.Boolean.falsy.union({"off"})


class SeriesSchema(Schema):
    series = fields.Integer()
    idx = fields.Float(missing=0.0)

    @pre_load
    def clean(self, data):
        if data["idx"] == "":
            data["idx"] = 0.0


class BookSchema(Schema):
    title = fields.String()
    isbn = fields.String()
    format = fields.Integer()
    released = fields.Integer()
    price = fields.Float()
    page_count = fields.Integer()
    read = MyBoolean(missing=False)
    authors = fields.List(fields.Integer())
    genres = fields.List(fields.Integer())
    publishers = fields.List(fields.Integer())
    languages = fields.List(fields.Integer())
    series = fields.Nested(SeriesSchema, many=True)

    @pre_load
    def parse_series(self, in_data):
        if "series" in in_data.keys():
            in_data["series"] = json.loads(in_data.get("series"))
        return in_data

    class Meta:
        strict = True
