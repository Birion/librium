from functools import wraps
from secrets import token_urlsafe
from urllib.parse import urlparse, urljoin

import pendulum
from flask import (
    redirect,
    url_for,
    request,
    flash,
    abort,
    Blueprint,
    current_app,
    render_template,
    _request_ctx_stack,
    has_request_context,
)
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login.config import EXEMPT_METHODS
from flask_wtf import FlaskForm
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import HiddenField
from wtforms import PasswordField, StringField

from patches.database import User, db_session
from patches.utils import Email, password_generator

bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()
login_manager.login_message = None

current_user = LocalProxy(lambda: _get_user())


def _get_user():
    if has_request_context() and not hasattr(_request_ctx_stack.top, "user"):
        current_app.login_manager._load_user()

    return getattr(_request_ctx_stack.top, "user", None)


class Form(FlaskForm):
    username = StringField("name")
    password = PasswordField("password")
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ""

    def redirect(self, endpoint="index", **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_admin:
            # return current_app.login_manager.unauthorized()
            abort(401)
        return func(*args, **kwargs)

    return decorated_view


@login_manager.user_loader
def load_user(session_token):
    return User.query.filter_by(session_token=session_token).first()


@bp.route("/login", methods=("GET", "POST"))
def login():
    user = User.query.first()
    if not user:
        return redirect(url_for("setup.index"))
    form = Form()
    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if check_password_hash(user.password, form.password.data):
            login_user(user)

            flash("Logged in successfully.", "success")

            _next = request.args.get("next")

            if not is_safe_url(_next):
                return abort(400)

            return redirect(_next or url_for("main.index"))

        flash("Incorrect password!", "error")

        return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@bp.route("/reset", methods=("GET", "POST"))
def reset():
    error = None
    if request.method == "POST":
        user = User.query.filter(User.email == request.form["email"]).one_or_none()
        if not user:
            error = (
                f"Couldn't find a user with email {request.form['email']}.",
                "error",
            )

        if not error:
            user.token = token_urlsafe()
            user.token_timeout = pendulum.now("UTC").add(hours=6)
            message = render_template("misc/reset_request.html", user=user)
            email = Email(
                sender=current_app.config["EMAIL"],
                receiver=user.email,
                subject="Password reset requested",
                message=message,
            )
            email.send_message()
            db_session.commit()

            flash("Password reset successfully requested.")

            return redirect(url_for("main.index"))
        else:
            flash(*error)
            return redirect(url_for("auth.reset"))

    if request.query_string:
        user = User.query.filter(User.email == request.args["email"]).one_or_none()
        token = request.args["token"]

        if not user:
            error = (
                f"Couldn't find a user with email {request.args['email']}.",
                "error",
            )
        else:
            if pendulum.now("UTC") > user.token_timeout:
                error = (f"Token timed out.", "error")
            if user.token != token:
                error = (
                    f"Provided token doesn't correspond to the stored token.",
                    "error",
                )

        if error:
            flash(*error)
            return redirect(url_for("auth.reset"))

        password = password_generator(16)
        user.password = generate_password_hash(password)
        user.token = token_urlsafe()
        user.token_timeout = pendulum.from_timestamp(0, "UTC")

        message = render_template(
            "misc/reset_success.html", user=user, password=password
        )
        email = Email(
            sender=current_app.config["EMAIL"],
            receiver=user.email,
            subject="Password reset",
            message=message,
        )

        email.send_message()
        db_session.commit()

        flash("Password reset.")

        return redirect(url_for("main.index"))

    return render_template("user/reset.html")
