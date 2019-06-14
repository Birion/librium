from flask import Blueprint, jsonify

from librium.database.pony.db import *

bp = Blueprint("api", __name__, url_prefix="/api")


def get_data(table):
    return jsonify([{"name": item.name, "id": item.id} for item in table.select()])


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
