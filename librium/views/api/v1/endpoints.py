"""
API v1 endpoints for Librium.

This module provides the v1 API endpoints for the Librium application.
"""

import re
from datetime import datetime
from glob import glob
from pathlib import Path

from flask import abort, jsonify, send_file, url_for, request
from flask_jwt_extended import create_access_token, jwt_required
from marshmallow import fields
from marshmallow.fields import Integer, String
from webargs.flaskparser import use_args, use_kwargs
from werkzeug.datastructures import FileStorage

from librium.core.logging import get_logger
from librium.database.backup import (
    create_backup,
    delete_backup,
    list_backups,
    restore_from_backup,
)
from librium.services import (
    AuthenticationService,
    AuthorService,
    BookService,
    GenreService,
    LanguageService,
    PublisherService,
    SeriesService,
)
from librium.views.api.v1 import bp
from utils.export import run as export_func


logger = get_logger("api.v1.endpoints")


def get_data_from_service(service):
    """
    Get all items from a service and return as JSON.

    Args:
        service: The service to get items from

    Returns:
        JSON response with items
    """
    items = service.get_all()
    results = [{"name": item.name, "id": item.id} for item in items]
    return jsonify(results)


@bp.route("/series")
@jwt_required()
def series():
    logger.info("GET /api/v1/series called")
    """
    Get all series.

    Returns:
        JSON response with series
    """
    return get_data_from_service(SeriesService)


@bp.route("/genres")
@jwt_required()
def genres():
    logger.info("GET /api/v1/genres called")
    """
    Get all genres.

    Returns:
        JSON response with genres
    """
    return get_data_from_service(GenreService)


@bp.route("/languages")
@jwt_required()
def languages():
    logger.info("GET /api/v1/languages called")
    """
    Get all languages.

    Returns:
        JSON response with languages
    """
    return get_data_from_service(LanguageService)


@bp.route("/publishers")
@jwt_required()
def publishers():
    logger.info("GET /api/v1/publishers called")
    """
    Get all publishers.

    Returns:
        JSON response with publishers
    """
    return get_data_from_service(PublisherService)


@bp.route("/add", methods=["POST"])
@jwt_required()
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
        logger.warning("Missing name in add endpoint")
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
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "suffix": "",
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
                logger.warning(f"Author {args['name']} already exists")
                return abort(403, f"Author {args['name']} already exists")

        # Create the author using the service
        new_item = AuthorService.create(**{k: v for k, v in options.items() if v})
        logger.info(f"Created new author: {args['name']} (ID: {new_item.id})")
    else:
        # Check if item exists by name
        existing_items = [
            item for item in service.get_all() if item.name == args["name"]
        ]
        if existing_items:
            logger.warning(f"Object {args['name']} already exists in {args['type']}")
            return abort(403, "Object already exists")

        # Create the item using the service
        new_item = service.create(name=args["name"])
        logger.info(f"Created new {args['type']}: {args['name']} (ID: {new_item.id})")

    return jsonify({"id": new_item.id, "name": args["name"]})


@bp.route("/delete", methods=["POST"])
@jwt_required()
@use_args({"id": Integer(required=True)}, location="form")
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
            logger.info(f"Deleting cover file for book {book.id} ({cover_file})")
            cover_file.unlink()

        # Delete the book using the service
        BookService.delete(args["id"])
    else:
        logger.warning(f"Book with ID {args['id']} not found for deletion")
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
@jwt_required()
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
    logger.info(f"POST /api/v1/add/cover called with uuid: {uuid}, cover: {cover}")
    # Get the book using the service
    book = BookService.get_by_uuid(uuid)
    if not book:
        logger.warning(f"Book with uuid {uuid} not found for cover upload")
        return jsonify({"response": "Book not found"}), 404

    # Save the cover file
    covers_dir = get_directory("covers")
    try:
        with open(covers_dir / f"{book.uuid}.jpg", "wb") as fp:
            cover.save(fp)
        logger.info(f"Cover uploaded for book {book.id} (uuid: {book.uuid})")
    except Exception as e:
        logger.exception(
            f"Failed to save cover for book {book.id} (uuid: {book.uuid}): {e}"
        )
        return jsonify({"response": "Failed to save cover"}), 500

    # Update the book if needed
    if not book.has_cover:
        BookService.update(book.id, has_cover=True)
        logger.info(f"Book {book.id} updated to has_cover=True")

    return jsonify({"response": "OK"})


@bp.route("/export")
@jwt_required()
@use_kwargs({"format": String(required=False)}, location="query")
def export(format=None):
    """
    Export books to the specified format.

    Args:
        format: The format to export to (csv or json), defaults to csv

    Returns:
        File download in the specified format
    """
    logger.info(f"GET /api/v1/export called with format: {format}")
    # Default to CSV if no format is specified
    if format is None:
        format = "csv"

    # Validate format
    if format not in ["csv", "json"]:
        logger.warning(f"Invalid export format requested: {format}")
        return jsonify({"error": "Invalid format. Supported formats: csv, json"}), 400

    try:
        tempfile = export_func(format)
        logger.info(f"Exported books to {format}, file: {tempfile}")
        return send_file(
            tempfile,
            as_attachment=True,
            download_name=f"export.{format}",
            mimetype="text/csv" if format == "csv" else "application/json",
        )
    except Exception as e:
        logger.exception(f"Failed to export books to {format}: {e}")
        return jsonify({"error": f"Failed to export books: {str(e)}"}), 500


# Database backup and restore endpoints


@bp.route("/backup/create", methods=["POST"])
@jwt_required()
@use_kwargs({"filename": String(required=False)}, location="form")
def backup_create(filename=None):
    """
    Create a backup of the database.

    Args:
        filename: Optional name for the backup file

    Returns:
        JSON response with the backup file path
    """
    logger.info(f"POST /api/v1/backup/create called with filename: {filename}")
    try:
        backup_file = create_backup(filename)
        logger.info(f"Backup created successfully: {backup_file.name}")
        return jsonify(
            {
                "success": True,
                "message": "Backup created successfully",
                "filename": backup_file.name,
            }
        )
    except Exception as e:
        logger.exception(f"Error creating backup: {e}")
        return (
            jsonify({"success": False, "message": f"Error creating backup: {str(e)}"}),
            500,
        )


@bp.route("/backup/list", methods=["GET"])
@jwt_required()
def backup_list():
    """
    List all available backups.

    Returns:
        JSON response with a list of backup files
    """
    logger.info("GET /api/v1/backup/list called")
    try:
        backups = list_backups()
        logger.info(f"Found {len(backups)} backups")
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
        logger.exception(f"Error listing backups: {e}")
        return (
            jsonify({"success": False, "message": f"Error listing backups: {str(e)}"}),
            500,
        )


@bp.route("/backup/restore", methods=["POST"])
@jwt_required()
@use_kwargs({"filename": String(required=True)}, location="form")
def backup_restore(filename):
    """
    Restore the database from backup.

    Args:
        filename: Backup file name or special keywords like 'latest', 'last', 'first'

    Returns:
        JSON response with the action result
    """
    logger.info(f"POST /api/v1/backup/restore called with filename: {filename}")
    try:
        if filename in ("latest", "last", "first"):
            glob_pattern = Path.cwd() / "backups" / "backup_*.sqlite"
            backup_files = [Path(x) for x in glob(str(glob_pattern))]
            backup_files.sort(
                key=lambda x: x.stat().st_mtime, reverse=filename in ("last", "first")
            )
            backup_file = Path(backup_files[0])
            logger.info(
                f"Requested to use {filename} backup. Using backup file: {backup_file}"
            )
        else:
            backup_dir = Path.cwd() / "backups"
            backup_file = backup_dir / filename

        if not backup_file.exists():
            logger.warning(f"Backup file {filename} not found for restore")
            return (
                jsonify(
                    {"success": False, "message": f"Backup file {filename} not found"}
                ),
                404,
            )

        success = restore_from_backup(backup_file)

        if success:
            logger.info(f"Database restored successfully from {backup_file}")
            return jsonify(
                {"success": True, "message": "Database restored successfully"}
            )
        else:
            logger.error(f"Error restoring database from {backup_file}")
            return (
                jsonify({"success": False, "message": "Error restoring database"}),
                500,
            )
    except Exception as e:
        logger.exception(f"Exception during database restore: {str(e)}")
        return (
            jsonify(
                {"success": False, "message": f"Error restoring database: {str(e)}"}
            ),
            500,
        )


@bp.route("/backup/delete", methods=["POST"])
@jwt_required()
@use_kwargs({"filename": String(required=True)}, location="form")
def backup_delete(filename):
    """
    Delete a backup file.

    Args:
        filename: The name of the backup file to delete

    Returns:
        JSON response with the action result
    """
    logger.info(f"POST /api/v1/backup/delete called with filename: {filename}")
    try:
        backup_dir = Path.cwd() / "backups"
        backup_file = backup_dir / filename

        if not backup_file.exists():
            logger.warning(f"Backup file {filename} not found for delete")
            return (
                jsonify(
                    {"success": False, "message": f"Backup file {filename} not found"}
                ),
                404,
            )

        success = delete_backup(backup_file)

        if success:
            logger.info(f"Backup {filename} deleted successfully")
            return jsonify(
                {"success": True, "message": f"Backup {filename} deleted successfully"}
            )
        else:
            logger.error(f"Error deleting backup {filename}")
            return (
                jsonify(
                    {"success": False, "message": f"Error deleting backup {filename}"}
                ),
                500,
            )
    except Exception as e:
        logger.exception(f"Exception during backup delete: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Error deleting backup: {str(e)}"}),
            500,
        )


# Authentication endpoints


@bp.route("/auth/token", methods=["POST"])
@use_kwargs(
    {"username": String(required=True), "password": String(required=True)},
    location="form",
)
def get_token(username, password):
    """
    Get JWT token. Example: {"username": "admin", "password": "admin"}
    """
    authenticator = AuthenticationService.get_by_name(username)
    if authenticator and authenticator.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401


@bp.route("/protected")
@jwt_required()
def protected():
    return jsonify(msg="You are authenticated!"), 200


# Error handlers for API
@bp.app_errorhandler(404)
def api_not_found(error):
    logger.warning(f"API 404 error: {request.path} - {error}")
    response = {"error": "Not found", "message": str(error)}
    return jsonify(response), 404


@bp.app_errorhandler(400)
def api_bad_request(error):
    logger.warning(f"API 400 error: {request.path} - {error}")
    response = {"error": "Bad request", "message": str(error)}
    return jsonify(response), 400


@bp.app_errorhandler(500)
def api_internal_error(error):
    logger.error(f"API 500 error: {request.path} - {error}")
    response = {"error": "Internal server error", "message": str(error)}
    return jsonify(response), 500


@bp.app_errorhandler(Exception)
def api_unhandled_exception(error):
    logger.exception(f"API unhandled exception: {error}")
    response = {"error": "Unexpected error", "message": str(error)}
    return jsonify(response), 500
