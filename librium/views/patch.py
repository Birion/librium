from csv import DictReader

import pendulum
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from patches.database import db_session, Advisory, Update, Customer, User
from .auth import admin_required
from .main import set_lists

bp = Blueprint("patch", __name__, url_prefix="/patch")
bp.before_request(set_lists)


@bp.route("/<pid>")
@login_required
def index(pid):
    advisory = Advisory.query.filter(Advisory.number == pid).one_or_none()
    if advisory:
        return render_template("patch/../templates/book/index.html", advisory=advisory)
    else:
        flash(f"No patch advisory with this number: {pid}.", "error")
    return redirect(url_for("patch.index"))


@bp.route("/create", methods=("GET", "POST"))
@admin_required
def create():
    if request.method == "POST":
        customer_id = int(request.form["customer"])
        assignee_id = (
            int(request.form["assignee"])
            if request.form["assignee"].isdigit()
            else None
        )
        _advisory = Advisory.query.filter(
            Advisory.number == request.form["number"]
        ).one_or_none()
        if not _advisory:
            u = Update(user_id=current_user.id, action="create")
            apar = Advisory(
                number=request.form["number"],
                customer_id=customer_id,
                author_id=current_user.id,
                target_date=pendulum.from_format(
                    request.form["target"], "YYYY-MM-DD"
                ).date(),
                assignee_id=assignee_id,
            )
            u.advisory = apar
            db_session.add(apar)
            db_session.commit()

            flash(f"Created APAR {request.form['number']}.", "success")
        else:
            flash(
                f"APAR {request.form['number']} already exists in the database!",
                "warning",
            )

        return redirect(url_for("main.index"))

    return render_template("patch/create/create.html")


@bp.route("/create/multiple", methods=("GET", "POST"))
@admin_required
def multiple():
    if request.method == "POST":
        success = 0
        advisories = [x for x in DictReader(request.form["advisories"].split("\n"))]
        for advisory in advisories:
            print(advisory)
            print(Customer.query.all())
            _advisory = Advisory.query.filter_by(
                number=advisory["number"]
            ).one_or_none()
            _customer = Customer.query.filter_by(
                name=advisory["customer"]
            ).one_or_none()
            print(_advisory)
            print(_customer)
            if not _customer:
                flash(f"No customer {advisory['customer']}!", "error")
                continue
            if _advisory:
                flash(f"Patch advisory {_advisory.number} already created!", "warning")
                continue
            u = Update(user_id=current_user.id, action="create")
            apar = Advisory(
                number=advisory["number"],
                customer=_customer,
                author=current_user,
                target_date=pendulum.from_format(
                    advisory["target"], "YYYY-MM-DD"
                ).date(),
            )
            u.advisory = apar
            db_session.add(apar)
            success += 1
        db_session.commit()
        flash(f"{success} patch advisories created.", "success")
        return redirect(url_for("main.index"))
    return render_template("patch/create/multiple.html")


@bp.route("/<pid>/update", methods=("GET", "POST"))
@login_required
def update(pid):
    if request.method == "POST":
        error = None
        f = request.form

        customer = Customer.query.filter_by(name=f.get("customer")).one_or_none()
        assignee_id = f.get("assignee", "")
        assignee_id = int(assignee_id) if assignee_id.isdigit() else None
        if assignee_id:
            assignee = User.query.filter_by(id=assignee_id).one_or_none()
        else:
            assignee = None
        change = f.get("change", None)
        notes = f.get("notes", None)
        applicable = f.get("applicable", "")
        applicable = bool(int(applicable)) if applicable.isdigit() else None

        advisory = Advisory.query.filter(Advisory.number == pid).one_or_none()

        if not advisory:
            error = (f"Patch advisory {pid} doesn't exist!", "error")
        else:
            if customer:
                advisory.customer = customer
            advisory.assignee = assignee
            advisory.change = change
            advisory.notes = notes
            advisory.applicable = applicable
            if not applicable and applicable is not None:
                advisory.resolved = True

            if not len(db_session.dirty):
                error = (f"No updates for patch advisory {pid}.", "info")
            else:
                u = Update(
                    user_id=current_user.id, advisory_id=advisory.id, action="update"
                )
                db_session.add(u)
                db_session.commit()

        if error:
            flash(*error)

        return redirect(url_for("patch.index", pid=request.form["number"]))

    return redirect(url_for("main.index"))


@bp.route("/<pid>/resolve", methods=("GET", "POST"))
@login_required
def resolve(pid):
    if request.method == "POST":
        advisory = Advisory.query.filter_by(number=pid).one_or_none()
        error = None
        if advisory:
            if advisory.resolved:
                error = f"Patch advisory {pid} is already resolved!"
            advisory.resolve()
            u = Update(
                user_id=current_user.id, advisory_id=advisory.id, action="resolve"
            )
            db_session.add(u)
            db_session.commit()
        else:
            error = f"Patch advisory {pid} does not exist!"

        if error:
            flash(error, "error")

        return redirect(url_for("patch.index", pid=pid))

    return redirect(url_for("main.index"))


@bp.route("/<pid>/validate", methods=("GET", "POST"))
@admin_required
def validate(pid):
    if request.method == "POST":
        advisory = Advisory.query.filter_by(number=pid).one_or_none()
        error = None
        if advisory:
            if advisory.validated:
                error = f"Patch advisory {pid} is already validated!"
            advisory.validate()
            advisory.validator_id = current_user.id
            u = Update(
                user_id=current_user.id, advisory_id=advisory.id, action="validate"
            )
            db_session.add(u)
            db_session.commit()
        else:
            error = f"Patch advisory {pid} does not exist!"

        if error:
            flash(error, "error")

        return redirect(url_for("patch.index", pid=pid))

    return redirect(url_for("main.index"))
