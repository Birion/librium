from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash

from patches.database import User, db_session
from .main import set_lists

bp = Blueprint("user", __name__, url_prefix="/user")
bp.before_request(set_lists)


def get_user(args: dict) -> tuple:
    uid = args.get("uid", None)
    return User.query.filter_by(id=uid).one_or_none() if uid else current_user, uid


@bp.route("/profile")
@login_required
def profile():
    user, uid = get_user(request.args)
    error = None

    if not user:
        error = f"User with id {uid} doesn't exist.", "error"
    if not current_user.is_admin and user != current_user:
        error = "You cannot access someone else's profile!", "error"

    if not error:
        return render_template("user/profile.html", user=user)
    else:
        flash(*error)
        return redirect(url_for("main.index"))


@bp.route("/password/change", methods=["GET", "POST"])
@login_required
def change():
    user, uid = get_user(request.args)
    error = None

    if not user:
        error = f"User with id {uid} doesn't exist.", "error"
    if not current_user.is_admin and user != current_user:
        error = "You cannot change someone else's password!", "error"

    if request.method == "POST":
        if check_password_hash(user.password, request.form["oldpwd"]):
            user.change_password(request.form["newpwd1"])
            user.refresh_session()

            db_session.commit()

            flash("Password changed successfully. Please log in again!", "success")

            return redirect(url_for("main.index"))

    if not error:
        return render_template("user/change.html", user=user)
    else:
        flash(*error)
        return redirect(url_for("main.index"))
