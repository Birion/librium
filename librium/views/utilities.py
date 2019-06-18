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
    title = fields.String(required=False)
    isbn = fields.String(required=False)
    format = fields.Integer(required=False)
    released = fields.Integer(required=False)
    price = fields.Float(required=False)
    page_count = fields.Integer(required=False)
    read = MyBoolean(missing=False)
    authors = fields.List(fields.Integer(), required=False)
    genres = fields.List(fields.Integer(), required=False)
    publishers = fields.List(fields.Integer(), required=False)
    languages = fields.List(fields.Integer(), required=False)
    series = fields.Nested(SeriesSchema, many=True, required=False)

    @pre_load
    def parse_series(self, in_data):
        if "series" in in_data.keys():
            in_data["series"] = json.loads(in_data.get("series"))
        if "isbn" in in_data.keys():
            in_data["isbn"] = in_data["isbn"].replace("-", "")
        return in_data

    class Meta:
        strict = True
