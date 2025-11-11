"""
API v1 endpoints for Librium.

This module provides the v1 API endpoints for the Librium application.
"""

import re
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path

from flask import jsonify, request, send_file, url_for
from flask_jwt_extended import create_access_token, jwt_required
from flask_limiter import ExemptionScope
from webargs.flaskparser import use_args, use_kwargs

from librium.core.limit import limiter
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
from librium.views.api.errors import (
    bad_request,
    conflict,
    forbidden,
    internal_server_error,
    not_found,
    unauthorized,
)
from librium.views.api.v1 import bp
from librium.views.api.v1.schemas import (
    AuthTokenSchema,
    BackupCreateSchema,
    BackupDeleteSchema,
    BackupRestoreSchema,
    BookIdSchema,
    BooksQuerySchema,
    CoverFileSchema,
    CoverSchema,
    EntitySchema,
    ExportSchema,
)
from utils.export import run as export_func

logger = get_logger("api.v1.endpoints")

# limiter.limit("100/day;30/hour;5/minute")(bp)

# More restrictive limits for backup operations (resource-intensive)
limiter.limit("10/day;5/hour;2/minute", override_defaults=True)(
    lambda: request.path.startswith("/api/v1/backup/")
)

# More restrictive limits for data modification endpoints (POST methods)
limiter.limit("50/day;20/hour;3/minute", override_defaults=True)(
    lambda: request.method == "POST" and request.path.startswith("/api/v1/")
)


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
    EntitySchema,
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
    if not args.get("name") and args.get("type") != "author":
        logger.warning("Missing name in add endpoint")
        return forbidden("Missing name")

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
            "first_name": args.get("first_name", ""),
            "middle_name": args.get("middle_name", ""),
            "last_name": args.get("last_name", ""),
            "prefix": args.get("prefix", ""),
            "suffix": args.get("suffix", ""),
        }
        args["name"] = args["name"] or " ".join(
            (
                options["first_name"],
                options["middle_name"],
                options["last_name"],
                options["prefix"],
                options["suffix"],
            )
        )
        author = args["name"].split()
        for section in author:
            if re.search(r"^[a-z]", section):
                idx = author.index(section)
                author[idx] = author.pop(idx) + " " + author[idx]
        if len(author) >= 1 and author[-1] in ["Jr", "Jr.", "III", "III."]:
            options["suffix"] = author.pop(-1)

        if len(author) == 1:
            options["last_name"] = author[0]
        elif len(author) > 1:
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
                return conflict(f"Author {args['name']} already exists")

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
            return conflict(
                f"{args['type'].capitalize()} '{args['name']}' already exists"
            )

        # Create the item using the service
        new_item = service.create(name=args["name"])
        logger.info(f"Created new {args['type']}: {args['name']} (ID: {new_item.id})")

    return jsonify({"id": new_item.id, "name": args["name"]})


@bp.route("/delete", methods=["POST"])
@jwt_required()
@use_args(BookIdSchema, location="form")
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
@use_kwargs(CoverSchema, location="form")
@use_kwargs(CoverFileSchema, location="files")
@jwt_required()
def add_cover(**kwargs):
    """
    Add a cover image for a book.

    Args:
        args: The validated request arguments containing cover and uuid

    Returns:
        JSON response indicating success or failure
    """
    cover = kwargs["cover"]
    uuid = kwargs["uuid"]
    logger.info(f"POST /api/v1/add/cover called with uuid: {uuid}, cover: {cover}")
    # Get the book using the service
    book = BookService.get_by_uuid(uuid)
    if not book:
        logger.warning(f"Book with uuid {uuid} not found for cover upload")
        return not_found(f"Book with UUID {uuid} not found")

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
        return internal_server_error(f"Failed to save cover: {str(e)}")

    # Update the book if needed
    if not book.has_cover:
        BookService.update(book.id, has_cover=True)
        logger.info(f"Book {book.id} updated to has_cover=True")

    return jsonify({"response": "OK"})


@bp.route("/export")
@jwt_required()
@use_args(ExportSchema, location="query")
def export(args):
    """
    Export books to the specified format.

    Args:
        args: The validated request arguments containing optional format

    Returns:
        File download in the specified format
    """
    format = args.get("format")
    logger.info(f"GET /api/v1/export called with format: {format}")
    # Default to CSV if no format is specified
    if format is None:
        format = "csv"

    # Format validation is handled by the schema, but we'll keep this check for safety
    if format not in ["csv", "json"]:
        logger.warning(f"Invalid export format requested: {format}")
        return bad_request("Invalid format. Supported formats: csv, json")

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
        return internal_server_error(f"Failed to export books: {str(e)}")


# Database backup and restore endpoints


@bp.route("/backup/create", methods=["POST"])
@jwt_required()
@use_args(BackupCreateSchema, location="form")
def backup_create(args):
    """
    Create a backup of the database.

    Args:
        args: The validated request arguments containing optional filename

    Returns:
        JSON response with the backup file path
    """
    filename = args.get("filename")
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
        return internal_server_error(f"Error creating backup: {str(e)}")


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
        return internal_server_error(f"Error listing backups: {str(e)}")


@bp.route("/backup/restore", methods=["POST"])
@jwt_required()
@use_args(BackupRestoreSchema, location="form")
def backup_restore(args):
    """
    Restore the database from backup.

    Args:
        args: The validated request arguments containing filename

    Returns:
        JSON response with the action result
    """
    filename = args["filename"]
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
            return not_found(f"Backup file {filename} not found")

        success = restore_from_backup(backup_file)

        if success:
            logger.info(f"Database restored successfully from {backup_file}")
            return jsonify(
                {"success": True, "message": "Database restored successfully"}
            )
        else:
            logger.error(f"Error restoring database from {backup_file}")
            return internal_server_error("Error restoring database")
    except Exception as e:
        logger.exception(f"Exception during database restore: {str(e)}")
        return internal_server_error(f"Error restoring database: {str(e)}")


@bp.route("/backup/delete", methods=["POST"])
@jwt_required()
@use_args(BackupDeleteSchema, location="form")
def backup_delete(args):
    """
    Delete a backup file.

    Args:
        args: The validated request arguments containing filename

    Returns:
        JSON response with the action result
    """
    filename = args["filename"]
    logger.info(f"POST /api/v1/backup/delete called with filename: {filename}")
    try:
        backup_dir = Path.cwd() / "backups"
        backup_file = backup_dir / filename

        if not backup_file.exists():
            logger.warning(f"Backup file {filename} not found for delete")
            return not_found(f"Backup file {filename} not found")

        success = delete_backup(backup_file)

        if success:
            logger.info(f"Backup {filename} deleted successfully")
            return jsonify(
                {"success": True, "message": f"Backup {filename} deleted successfully"}
            )
        else:
            logger.error(f"Error deleting backup {filename}")
            return internal_server_error(f"Error deleting backup {filename}")
    except Exception as e:
        logger.exception(f"Exception during backup delete: {str(e)}")
        return internal_server_error(f"Error deleting backup: {str(e)}")


# Books endpoint
@bp.route("/books")
@jwt_required()
@use_args(BooksQuerySchema, location="query")
def books(args):
    """
    Get books with filtering and sorting options.

    Args:
        args: The validated request arguments containing filtering and sorting options

    Returns:
        JSON response with books and pagination information
    """
    logger.info(f"GET /api/v1/books called with args: {args}")

    try:
        # Get books using the BookService
        books, total_count = BookService.get_paginated(
            page=args.get("page", 1),
            page_size=args.get("page_size", 30),
            filter_read=args.get("read"),
            search=args.get("search"),
            start_with=args.get("start_with"),
            sort_by=args.get("sort_by", "title"),
            sort_order=args.get("sort_order", "asc"),
        )

        # Calculate pagination information
        total_pages = (total_count + args.get("page_size", 30) - 1) // args.get(
            "page_size", 30
        )

        # Convert books to dictionaries
        book_dicts = []
        for book in books:
            book_dict = {
                "id": book.id,
                "title": book.title,
                "uuid": book.uuid,
                "isbn": book.isbn,
                "released": book.released,
                "price": float(book.price) if book.price else None,
                "page_count": book.page_count,
                "read": book.read,
                "has_cover": book.has_cover,
                "format": (
                    {"id": book.format.id, "name": book.format.name}
                    if book.format
                    else None
                ),
                "authors": [
                    {"id": a.author.id, "name": a.author.name} for a in book.authors
                ],
                "genres": [{"id": g.id, "name": g.name} for g in book.genres],
                "publishers": [{"id": p.id, "name": p.name} for p in book.publishers],
                "languages": [{"id": l.id, "name": l.name} for l in book.languages],
                "series": [
                    {"id": s.series.id, "name": s.series.name, "index": s.index}
                    for s in book.series
                ],
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None,
            }
            book_dicts.append(book_dict)

        # Return the response
        return jsonify(
            {
                "books": book_dicts,
                "pagination": {
                    "page": args.get("page", 1),
                    "page_size": args.get("page_size", 30),
                    "total_items": total_count,
                    "total_pages": total_pages,
                },
                "filters": {
                    "read": args.get("read"),
                    "search": args.get("search"),
                    "start_with": args.get("start_with"),
                },
                "sorting": {
                    "sort_by": args.get("sort_by", "title"),
                    "sort_order": args.get("sort_order", "asc"),
                },
            }
        )
    except Exception as e:
        logger.exception(f"Error getting books: {e}")
        return internal_server_error(f"Error getting books: {str(e)}")


# Authentication endpoints
@bp.route("/auth/token", methods=["POST"])
@limiter.limit(
    "20/day;5/hour;3/minute"
)  # More restrictive limits for auth token endpoint
@use_args(AuthTokenSchema, location="form")
def get_token(args):
    """
    Get JWT token.

    Args:
        args: The validated request arguments containing username and password

    Returns:
        JSON response with access token or error message
    """
    username = args["username"]
    password = args["password"]
    authenticator = AuthenticationService.get_by_name(username)
    if authenticator and authenticator.check_password(password):
        access_token = create_access_token(
            identity=username, expires_delta=timedelta(days=365)
        )
        return jsonify(access_token=access_token)
    return unauthorized("Invalid credentials")


@bp.route("/protected")
@limiter.exempt  # Exempt this endpoint from rate limiting
@jwt_required()
def protected():
    return jsonify(msg="You are authenticated!"), 200


# Error handlers for API
@bp.app_errorhandler(404)
def api_not_found(error):
    logger.warning(f"API 404 error: {request.path} - {error}")
    return not_found(str(error))


@bp.app_errorhandler(400)
def api_bad_request(error):
    logger.warning(f"API 400 error: {request.path} - {error}")
    return bad_request(str(error))


@bp.app_errorhandler(500)
def api_internal_error(error):
    logger.error(f"API 500 error: {request.path} - {error}")
    return internal_server_error(str(error))


@bp.app_errorhandler(Exception)
def api_unhandled_exception(error):
    logger.exception(f"API unhandled exception: {error}")
    return internal_server_error(str(error))
