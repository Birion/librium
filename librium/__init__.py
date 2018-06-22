import os
import os.path

import connexion
from dotenv import load_dotenv, find_dotenv

from .__version__ import __version__
from .database import db_session
from .views import main

load_dotenv(find_dotenv())


def create_app(test_config=None):
    # create and configure the app
    app = connexion.App(__name__, specification_dir="./")
    app.add_api("swagger.yml", base_path="/api")

    application = app.app

    application.config.from_object(os.getenv("APP_SETTINGS"))
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # auth.login_manager.init_app(app)
    # auth.login_manager.login_view = "auth.login"
    #
    # app.jinja_env.globals["pendulum"] = pendulum
    # app.jinja_env.globals["re"] = re
    # app.jinja_env.filters["ed"] = ed

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
    application.add_url_rule("/", endpoint="index")

    return application


app = create_app()
