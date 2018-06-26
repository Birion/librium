import os
import os.path

import connexion
from dotenv import load_dotenv, find_dotenv
from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta

from librium.__version__ import __version__
from librium.database import db_session
from librium.views import main, book

load_dotenv(find_dotenv())


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(CustomJSONEncoder, self).default(obj)


def create_app(test_config=None):
    # create and configure the app
    app = connexion.App("librium", specification_dir="./")
    app.add_api("swagger.yml", base_path="/api")

    application = app.app

    application.config.from_object(os.getenv("APP_SETTINGS"))
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    application.json_encoder = CustomJSONEncoder

    if test_config is None:
        # load the instance config, if it exists, when not testing
        application.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        application.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass

    @application.template_global()
    def version():
        return __version__

    @application.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    application.register_blueprint(main.bp)
    application.register_blueprint(book.bp)
    application.add_url_rule("/", endpoint="index")

    return application


app = create_app()
