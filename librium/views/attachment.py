import io
import os.path
from hashlib import sha512

from flask import Blueprint, flash, redirect, request, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from patches.database import Advisory, Attachment, Update, db_session
from .auth import admin_required
from .main import set_lists

bp = Blueprint("attachment", __name__, url_prefix="/attachment")
bp.before_request(set_lists)

ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".xls",
    ".xlsx",
    ".ods",
}
MAXIMUM_LENGTH = 5 * 1024 * 1024


def allowed_file(filename):
    return (
        os.path.extsep in filename
        and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
    )


@bp.route("/<content_hash>/<filename>")
@login_required
def index(content_hash, filename):
    attachment = Attachment.query.filter_by(hash=content_hash).one_or_none()
    if attachment:
        contents = io.BytesIO(attachment.contents)
        return send_file(contents, mimetype=attachment.mimetype)
    else:
        flash("No such file.", "warning")

    return redirect(url_for("patch.index", pid=advisory.number))


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    advisory = Advisory.query.filter_by(id=request.form.get("id")).one_or_none()
    error = None
    contents = b""
    content_hash = sha512()
    file = request.files.get("upload", None)

    if not file:
        error = "Missing file"
    else:
        if file.filename == "":
            error = "No file selected"
        else:
            if not allowed_file(file.filename):
                error = f"You cannot upload files of {file.mimetype} format!"
            else:
                contents = file.stream.read()
                content_hash.update(contents)

                if len(contents) > MAXIMUM_LENGTH:
                    error = "The file you tried to upload is too big. Maximum filesize: 5 MB"

    if error:
        flash(error, "error")
    else:
        attachment = Attachment.query.filter_by(
            hash=content_hash.hexdigest()
        ).one_or_none()
        if not attachment:
            attachment = Attachment(
                filename=secure_filename(file.filename),
                hash=content_hash.hexdigest(),
                contents=contents,
                mimetype=file.mimetype,
                uploader=current_user,
            )
        attachment.advisories.append(advisory)
        update = Update(
            advisory=advisory, user=current_user, action="attach", attachment=attachment
        )

        if not attachment:
            db_session.add(attachment)
        db_session.add(update)
        db_session.commit()

        flash("Attachment successfully uploaded.")

    return redirect(url_for("patch.index", pid=advisory.number))


@bp.route("/remove", methods=["POST"])
@admin_required
def remove():
    data = request.get_json()
    pid = data.get("pid")
    content_hash = data.get("hash")
    advisory = Advisory.query.filter_by(number=pid).one_or_none()
    attachment = (
        Attachment.query.filter_by(hash=content_hash).filter_by(advisory=advisory).all()
    )
    if not attachment:
        flash("No attachment with this id.", "warning")
        return redirect(url_for("patch.index", pid=pid))

    update = Update(
        advisory=advisory, user=current_user, action="delete", attachment=attachment
    )

    attachment.advisories.remove(advisory)

    print(attachment.advisories)
    db_session.add(update)
    db_session.commit()

    return "OK"
