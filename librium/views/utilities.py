import simplejson as json

from marshmallow import pre_load, EXCLUDE, Schema, fields, INCLUDE
from webargs.fields import DelimitedList


class MyBoolean(fields.Boolean):
    truthy = fields.Boolean.truthy.union({"on"})
    falsy = fields.Boolean.falsy.union({"off"})


class SeriesSchema(Schema):
    series = fields.Integer(
        required=True,
        validate=lambda n: n > 0,
        error_messages={
            "required": "Series is required",
            "validator_failed": "Invalid series",
        },
    )
    idx = fields.Float(
        load_default=0.0,
        validate=lambda n: n >= 0,
        error_messages={"validator_failed": "Series index must be non-negative"},
    )

    @pre_load
    def clean(self, data, **kwargs):
        data = dict(data)
        if data["idx"] == "":
            data["idx"] = 0.0
        return data

    class Meta:
        unknown = INCLUDE


class BookSchema(Schema):
    title = fields.String(
        required=True,
        validate=lambda s: len(s.strip()) > 0,
        error_messages={
            "required": "Title is required",
            "validator_failed": "Title cannot be empty",
        },
    )
    isbn = fields.String(
        validate=lambda s: not s or (len(s) in [10, 13] and s.isdigit())
    )
    format = fields.Integer(
        required=True,
        validate=lambda n: n > 0,
        error_messages={
            "required": "Format is required",
            "validator_failed": "Invalid format",
        },
    )
    released = fields.Integer(validate=lambda n: not n or (n > 1000 and n < 3000))
    price = fields.Float(validate=lambda n: not n or n >= 0)
    page_count = fields.Integer(validate=lambda n: not n or n > 0)
    read = MyBoolean(load_default=False)
    authors = DelimitedList(
        fields.Integer(validate=lambda n: n > 0),
        required=True,
        error_messages={"required": "At least one author is required"},
    )
    genres = DelimitedList(fields.Integer(validate=lambda n: n > 0))
    publishers = DelimitedList(fields.Integer(validate=lambda n: n > 0))
    languages = DelimitedList(fields.Integer(validate=lambda n: n > 0))
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
