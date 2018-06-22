from flask import Blueprint, render_template, redirect, url_for, flash, request

from patches.database import User, Customer, db_session
from .main import set_lists

bp = Blueprint("setup", __name__, url_prefix="/setup")
bp.before_request(set_lists)

steps = [
    {"name": "setup", "text": "Start setup process", "icon": "id-badge"},
    {"name": "admin", "text": "Create admin account", "icon": "user-plus"},
    {"name": "customers", "text": "Add customers", "icon": "users"},
    {"name": "success", "text": "Finish the setup", "icon": "check"},
]


@bp.route("/")
def index():
    return redirect(url_for("setup.step", position=1))


@bp.route("/step/<int:position>", methods=["GET", "POST"])
def step(position):
    actual_step = position - 1
    if actual_step > len(steps):
        flash(f"No step {position} in the setup process.", "warning")
        return redirect(url_for("setup.index"))
    if request.method == "POST":
        current_step = steps[actual_step]["name"]
        form = request.form
        if current_step == "admin":
            u = (
                User.query.filter(User.active.is_(True))
                .filter(User.admin.is_(True))
                .first()
            )
            if u:
                flash("Admin user already created.", "warning")
                return redirect(url_for("setup.step", position=position + 1))
            user = User(
                email=form["email"],
                name=form["name"],
                surname=form["surname"],
                admin=True,
            )
            user.change_password(form["password"])
            user.make_username()
            db_session.add(user)
            db_session.commit()
        elif current_step == "customers":
            print(form)
            c = Customer.query.all()
            if c:
                flash("Customers already created.", "warning")
                return redirect(url_for("setup.step", position=position + 1))
            for customer in form["customers"].split("\n"):
                c = Customer(name=customer.strip())
                db_session.add(c)
            db_session.commit()
        return redirect(url_for("setup.step", position=position + 1))

    template = steps[actual_step]["name"]
    return render_template(f"setup/{template}.html", steps=steps)
