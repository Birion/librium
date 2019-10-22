import os
import os.path

from dotenv import find_dotenv, load_dotenv
from flask import Flask, url_for, request
from pony.flask import Pony

from librium.__version__ import __version__
from librium.views import book, main, api, covers
from .assets import assets
from .utils import parse_read_arg

load_dotenv(find_dotenv())


def create_app():
    app = Flask("librium")

    app.secret_key = os.getenv("SECRET_KEY")
    app.config.from_object(os.getenv("CONFIGURATION"))
    app.config["VERSION"] = __version__

    app.jinja_env.add_extension("jinja2.ext.do")

    pony = Pony()
    pony.init_app(app)

    assets.init_app(app)

    @app.route("/favicon.ico")
    def send_favicon():
        return app.send_static_file("img/favicon.ico")

    def url_for_self(**args):
        return url_for(request.endpoint, **dict(request.args, **args))

    app.jinja_env.globals["url_for_self"] = url_for_self
    app.jinja_env.filters["parse_read_arg"] = parse_read_arg

    app.register_blueprint(main.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(covers.bp)

    return app
