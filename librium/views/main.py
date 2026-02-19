from flask import Blueprint, redirect, render_template, request, url_for
from marshmallow import Schema, fields
from webargs.flaskparser import use_args

from librium.views.views import (
    get_authors,
    get_books,
    get_genres,
    get_series,
    get_years,
)

bp = Blueprint("main", __name__)


class UserArgs(Schema):
    page = fields.Integer()
    start = fields.String(required=False)
    read = fields.Boolean()
    id = fields.Integer()
    name = fields.String()
    search = fields.String()
    sort_by = fields.String()
    sort_order = fields.String(load_default="asc")


@bp.route("/")
@use_args(UserArgs, location="query")
def index(_args):
    def url_for_self(target, **args):
        return url_for(target, **dict(request.args, **args))

    return redirect(url_for_self("main.books"))


@bp.route("/a")
@use_args(UserArgs, location="query")
def authors(args):
    return render_template("main/index.html", **get_authors(args))


@bp.route("/s")
@use_args(UserArgs, location="query")
def series(args):
    return render_template("main/index.html", **get_series(args))


@bp.route("/b")
@use_args(UserArgs, location="query")
def books(args):
    return render_template("main/index.html", **get_books(args))


@bp.route("/y")
@use_args({"page": fields.Integer(), "year": fields.Integer()}, location="query")
def years(args):
    return render_template("main/index.html", **get_years(args))


@bp.route("/g")
@use_args(UserArgs, location="query")
def genres(args):
    return render_template("main/index.html", **get_genres(args))


@bp.route("/statistics")
def statistics():
    from librium.core.app import cache
    from librium.services import BookService

    @cache.cached(timeout=600)
    def get_cached_stats():
        return BookService.get_statistics()

    stats = get_cached_stats()
    return render_template("main/statistics.html", **stats)


@bp.route("/problems")
def problems():
    from librium.core.app import cache
    from librium.services import BookService

    @cache.cached(timeout=600)
    def get_cached_problems():
        return BookService.get_problems()

    problems = get_cached_problems()
    return render_template("main/problems.html", **problems)
