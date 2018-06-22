import json

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)

from patches.database import User, db_session, Customer
from patches.utils import Email, password_generator
from .auth import admin_required
from .main import set_lists

bp = Blueprint("admin", __name__, url_prefix="/admin")
bp.before_request(set_lists)


@bp.route("/")
@admin_required
def index():
    return redirect(url_for("admin.active"))


@bp.route("/users/inactive")
@admin_required
def inactive():
    users = User.query.filter(User.active.is_(False)).all()
    return render_template("admin/users/main.html", users=users)


@bp.route("/users/active")
@admin_required
def active():
    users = User.query.filter(User.active.is_(True)).all()
    return render_template("admin/users/main.html", users=users)


@bp.route("/user/activate/<int:uid>")
@admin_required
def activate(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    if user:
        user.is_active = True
        db_session.commit()
    else:
        flash("No user with this userid.", "warning")
    return redirect(url_for("admin.inactive"))


@bp.route("/user/deactivate/<int:uid>")
@admin_required
def deactivate(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    if user:
        user.is_active = False
        db_session.commit()
    else:
        flash("No user with this userid.", "warning")
    return redirect(url_for("admin.active"))


@bp.route("/user/new", methods=["GET", "POST"])
@admin_required
def user_new():
    if request.method == "POST":
        f = request.form
        name = f.get("name")
        surname = f.get("surname")
        address = f.get("email")
        admin = f.get("admin") == "on"
        password = password_generator(16)

        user = User(email=address, name=name, surname=surname, admin=admin)

        user.make_username()
        user.change_password(password)

        db_session.add(user)

        db_session.commit()

        message = render_template(
            "admin/email/create.html", user=user, password=password
        )

        email = Email(
            sender=current_app.config["EMAIL"],
            receiver=address,
            subject="New user created",
            message=message,
        )

        email.send_message()

        flash(f"New user {user.username} created.", "success")

        return redirect(url_for("admin.index"))

    return render_template("admin/users/profile.html")


@bp.route("/user/update/<int:uid>", methods=["GET", "POST"])
@admin_required
def user_update(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    if request.method == "POST":
        f = request.form
        name = f.get("name")
        surname = f.get("surname")
        email = f.get("email")
        admin = f.get("admin") == "on"

        user.name = name
        user.surname = surname
        user.admin = admin
        user.email = email

        user.make_username()

        db_session.commit()

        return redirect(url_for("admin.index"))

    return render_template("admin/users/profile.html", user=user)


@bp.route("/user/reset/password/<int:uid>")
@admin_required
def reset_password(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    password = password_generator(16)
    user.change_password(password)
    db_session.commit()

    message = render_template("admin/email/reset.html", user=user, password=password)

    email = Email(
        sender=current_app.config["EMAIL"],
        receiver=user.email,
        subject="Password reset",
        message=message,
    )

    email.send_message()

    flash(f"Password for {user.username} successfully changed.", "success")

    return redirect(url_for("admin.index"))


@bp.route("/user/reset/timeout/<int:uid>")
@admin_required
def reset_timeout(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    user.reset_timeout()
    db_session.commit()


@bp.route("/user/reset/token/<int:uid>")
@admin_required
def reset_token(uid):
    user = User.query.filter_by(id=uid).one_or_none()
    user.refresh_session()
    db_session.commit()


@bp.route("/customers")
def customers():
    return render_template("admin/customers/main.html")


@bp.route("/customer/new", methods=["POST"])
def customer_new():
    f = request.form
    c_new = f.get("customer")
    if c_new:
        c = Customer(name=c_new)
        db_session.add(c)
        db_session.commit()
    return redirect(url_for("admin.customers"))


@bp.route("/customer/update", methods=["POST"])
def customer_update():
    f = request.form
    cid = f.get("id")
    customer = (
        Customer.query.filter_by(id=int(cid)).one_or_none() if cid.isdigit() else None
    )
    if customer:
        action = f.get("action")
        if action == "update":
            customer.name = f.get("val")
        elif action == "decom":
            customer.decommission()
        elif action == "recom":
            customer.recommission()
        db_session.commit()
        return (
            json.dumps({"success": True, "name": customer.name, "action": action}),
            200,
            {"ContentType": "application/json"},
        )
    return json.dumps({"success": False}), 400, {"ContentType": "application/json"}
