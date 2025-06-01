"""
API v1 endpoints for Librium.

This module provides the v1 API endpoints for the Librium application.
"""

import re
from datetime import datetime
from pathlib import Path

from flask import abort, jsonify, send_file, url_for, request, current_app
from marshmallow import fields
from marshmallow.fields import Integer, String
from webargs.flaskparser import use_args, use_kwargs
from werkzeug.datastructures import FileStorage

from librium.services import (
    BookService,
    FormatService,
    GenreService,
    LanguageService,
    PublisherService,
    SeriesService,
    AuthorService,
)
from librium.database.backup import (
    create_backup,
    restore_from_backup,
    list_backups,
    delete_backup,
)
from librium.views.api.v1 import bp
from utils.export import run as export_func


def get_data_from_service(service):
    """
    Get all items from a service and return as JSON.

    Args:
        service: The service to get items from

    Returns:
        JSON response with items
    """
    items = service.get_all()
    return jsonify([{"name": item.name, "id": item.id} for item in items])


@bp.route("/series")
def series():
    """
    Get all series.

    Returns:
        JSON response with series
    """
    return get_data_from_service(SeriesService)


@bp.route("/genres")
def genres():
    """
    Get all genres.

    Returns:
        JSON response with genres
    """
    return get_data_from_service(GenreService)


@bp.route("/languages")
def languages():
    """
    Get all languages.

    Returns:
        JSON response with languages
    """
    return get_data_from_service(LanguageService)


@bp.route("/publishers")
def publishers():
    """
    Get all publishers.

    Returns:
        JSON response with publishers
    """
    return get_data_from_service(PublisherService)


@bp.route("/add", methods=["POST"])
@use_args(
    {"type": fields.String(required=True), "name": fields.String(required=True)},
    location="form",
)
def add(args):
    """
    Add a new item.

    Args:
        args: The request arguments

    Returns:
        JSON response with the new item
    """
    if args["name"] == "":
        return abort(403, "Missing name")

    # Map the type to the appropriate service
    service_lookup = {
        "genre": GenreService,
        "publisher": PublisherService,
        "language": LanguageService,
        "series": SeriesService,
        "author": AuthorService,
    }

    service = service_lookup[args["type"]]

    # Check if the item already exists
    # For authors, we'll need to check differently
    if args["type"] == "author":
        # Parse the author name
        options = {
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "suffix": None,
        }
        author = args["name"].split()
        for section in author:
            if re.search(r"^[a-z]", section):
                idx = author.index(section)
                author[idx] = author.pop(idx) + " " + author[idx]
        if author[-1] in ["Jr", "Jr.", "III", "III."]:
            options["suffix"] = author.pop(-1)

        if len(author) == 1:
            options["last_name"] = author[0]
        else:
            (
                options["first_name"],
                *options["middle_name"],
                options["last_name"],
            ) = author
        if options["middle_name"]:
            options["middle_name"] = " ".join(options["middle_name"])

        # Check if author exists by last name prefix (simplified check)
        existing_authors = AuthorService.get_by_last_name_prefix(options["last_name"])
        if existing_authors:
            # Check if any of the existing authors match exactly
            if AuthorService.get_by_full_name(**options) is not None:
                return abort(403, "Author already exists")

        # Create the author using the service
        new_item = AuthorService.create(**{k: v for k, v in options.items() if v})
    else:
        # Check if item exists by name
        existing_items = [
            item for item in service.get_all() if item.name == args["name"]
        ]
        if existing_items:
            return abort(403, "Object already exists")

        # Create the item using the service
        new_item = service.create(name=args["name"])

    return jsonify({"id": new_item.id, "name": args["name"]})


@bp.route("/delete", methods=["POST"])
@use_args({"id": Integer()}, location="form")
def delete(args):
    """
    Delete a book.

    Args:
        args: The request arguments

    Returns:
        JSON response with the redirect URL
    """
    book = BookService.get_by_id(args["id"])
    if book:
        # Delete the cover file if it exists
        covers_dir = get_directory("covers")
        cover_file = covers_dir / f"{book.uuid}.jpg"
        if cover_file.exists():
            cover_file.unlink()

        # Delete the book using the service
        BookService.delete(args["id"])

    return jsonify({"url": url_for("main.index")})


def get_directory(directory):
    """
    Get or create a directory.

    Args:
        directory: The directory name

    Returns:
        The directory path
    """
    p = Path.cwd() / directory
    p.mkdir(exist_ok=True)
    return p


@bp.route("/add/cover", methods=["POST"])
@use_kwargs({"cover": fields.Raw(required=True)}, location="files")
@use_kwargs({"uuid": fields.String(required=True)}, location="form")
def add_cover(cover: FileStorage, uuid):
    """
    Add a cover image for a book.

    Args:
        cover: The cover image file
        uuid: The book UUID

    Returns:
        JSON response indicating success or failure
    """
    # Get the book using the service
    book = BookService.get_by_uuid(uuid)
    if not book:
        return jsonify({"response": "Book not found"}), 404

    # Save the cover file
    covers_dir = get_directory("covers")
    with open(covers_dir / f"{book.uuid}.jpg", "wb") as fp:
        cover.save(fp)

    # Update the book if needed
    if not book.has_cover:
        BookService.update(book.id, has_cover=True)

    return jsonify({"response": "OK"})


@bp.route("/export")
def export():
    """
    Export books to CSV.

    Returns:
        CSV file download
    """
    tempfile = export_func()
    return send_file(tempfile, as_attachment=True, download_name="export.csv")


# Database backup and restore endpoints


@bp.route("/backup/create", methods=["POST"])
@use_kwargs({"filename": String(required=False)}, location="form")
def backup_create(filename=None):
    """
    Create a backup of the database.

    Args:
        filename: Optional name for the backup file

    Returns:
        JSON response with the backup file path
    """
    try:
        backup_file = create_backup(filename)
        return jsonify(
            {
                "success": True,
                "message": "Backup created successfully",
                "filename": backup_file.name,
            }
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error creating backup: {str(e)}"}),
            500,
        )


@bp.route("/backup/list", methods=["GET"])
def backup_list():
    """
    List all available backups.

    Returns:
        JSON response with a list of backup files
    """
    try:
        backups = list_backups()
        return jsonify(
            {
                "success": True,
                "backups": [
                    {
                        "filename": backup.name,
                        "path": str(backup),
                        "size": backup.stat().st_size,
                        "created": datetime.fromtimestamp(
                            backup.stat().st_mtime
                        ).isoformat(),
                    }
                    for backup in backups
                ],
            }
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error listing backups: {str(e)}"}),
            500,
        )


@bp.route("/backup/restore", methods=["POST"])
@use_kwargs({"filename": String(required=True)}, location="form")
def backup_restore(filename):
    """
    Restore the database from a backup.

    Args:
        filename: The name of the backup file

    Returns:
        JSON response indicating success or failure
    """
    try:
        backup_dir = Path.cwd() / "backups"
        backup_file = backup_dir / filename

        if not backup_file.exists():
            return (
                jsonify(
                    {"success": False, "message": f"Backup file {filename} not found"}
                ),
                404,
            )

        success = restore_from_backup(backup_file)

        if success:
            return jsonify(
                {"success": True, "message": "Database restored successfully"}
            )
        else:
            return (
                jsonify({"success": False, "message": "Error restoring database"}),
                500,
            )
    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error restoring database: {str(e)}"}
            ),
            500,
        )


@bp.route("/backup/delete", methods=["POST"])
@use_kwargs({"filename": String(required=True)}, location="form")
def backup_delete(filename):
    """
    Delete a backup file.

    Args:
        filename: The name of the backup file

    Returns:
        JSON response indicating success or failure
    """
    try:
        backup_dir = Path.cwd() / "backups"
        backup_file = backup_dir / filename

        if not backup_file.exists():
            return (
                jsonify(
                    {"success": False, "message": f"Backup file {filename} not found"}
                ),
                404,
            )

        success = delete_backup(backup_file)

        if success:
            return jsonify(
                {"success": True, "message": f"Backup {filename} deleted successfully"}
            )
        else:
            return (
                jsonify(
                    {"success": False, "message": f"Error deleting backup {filename}"}
                ),
                500,
            )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error deleting backup: {str(e)}"}),
            500,
        )
