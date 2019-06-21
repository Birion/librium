import re

from flask import Blueprint, jsonify, abort
from marshmallow import fields
from webargs.flaskparser import use_args

from librium.database.pony.db import *

bp = Blueprint("api", __name__, url_prefix="/api")


def get_data(table):
    return jsonify(
        [{"name": item.name, "id": item.id} for item in select(i for i in table)]
    )


@bp.route("/series")
def series():
    return get_data(Series)


@bp.route("/genres")
def genres():
    return get_data(Genre)


@bp.route("/languages")
def languages():
    return get_data(Language)


@bp.route("/publishers")
def publishers():
    return get_data(Publisher)


@bp.route("/add", methods=["POST"])
@use_args({"type": fields.String(required=True), "name": fields.String(required=True)})
def add(args):
    print(args)
    if args["name"] == "":
        return abort(403, "Missing name")
    lookup_table = {
        "genre": Genre,
        "publisher": Publisher,
        "language": Language,
        "series": Series,
        "author": Author,
    }
    table = lookup_table[args["type"]]
    if table.get(name=args["name"]):
        return abort(403, "Object already exists")

    if args["type"] == "author":
        options = {
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "suffix": None,
        }
        author = args["name"].split()
        for section in author:
            if re.search(r"^[a-z]", section):
                idx = author.index(section)
                author[idx] = author.pop(idx) + " " + author[idx]
        if author[-1] in ["Jr", "Jr.", "III", "III."]:
            options["suffix"] = author.pop(-1)

        if len(author) == 1:
            options["last_name"] = author[0]
        else:
            options["first_name"], *options["middle_name"], options[
                "last_name"
            ] = author
        if options["middle_name"]:
            options["middle_name"] = " ".join(options["middle_name"])
        new_item = table(**{k: v for k, v in options.items() if v})
    else:
        new_item = table(name=args["name"])

    commit()

    return jsonify({"id": new_item.id, "name": args["name"]})
