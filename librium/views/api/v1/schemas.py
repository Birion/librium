"""
API validation schemas for Librium.

This module provides validation schemas for the API endpoints.
"""

from marshmallow import Schema, validate
from marshmallow.fields import Boolean, Integer, Raw, String


class EntitySchema(Schema):
    """Schema for validating entity creation requests."""

    type = String(
        required=True,
        validate=validate.OneOf(
            ["genre", "publisher", "language", "series", "author"],
            error="Type must be one of: genre, publisher, language, series, author",
        ),
    )
    name = String(required=True, validate=validate.Length(min=1, max=255))


class BookIdSchema(Schema):
    """Schema for validating book ID requests."""

    id = Integer(required=True, validate=validate.Range(min=1))


class CoverSchema(Schema):
    """Schema for validating cover upload requests."""

    cover = Raw(required=True)
    uuid = String(
        required=True,
        validate=validate.Regexp(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            error="UUID must be in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        ),
    )


class ExportSchema(Schema):
    """Schema for validating export requests."""

    format = String(
        required=False,
        validate=validate.OneOf(
            ["csv", "json"], error="Format must be one of: csv, json"
        ),
    )


class BackupCreateSchema(Schema):
    """Schema for validating backup creation requests."""

    filename = String(
        required=False,
        validate=validate.Regexp(
            r"^[a-zA-Z0-9_\-\.]+$",
            error="Filename must contain only alphanumeric characters, underscores, hyphens, and periods",
        ),
    )


class BackupRestoreSchema(Schema):
    """Schema for validating backup restore requests."""

    filename = String(
        required=True,
        validate=validate.Regexp(
            r"^[a-zA-Z0-9_\-\.]+$|^latest$|^last$|^first$",
            error="Filename must contain only alphanumeric characters, underscores, hyphens, and periods, or be one of: latest, last, first",
        ),
    )


class BackupDeleteSchema(Schema):
    """Schema for validating backup delete requests."""

    filename = String(
        required=True,
        validate=validate.Regexp(
            r"^[a-zA-Z0-9_\-\.]+$",
            error="Filename must contain only alphanumeric characters, underscores, hyphens, and periods",
        ),
    )


class AuthTokenSchema(Schema):
    """Schema for validating authentication token requests."""

    username = String(required=True, validate=validate.Length(min=1, max=255))
    password = String(required=True, validate=validate.Length(min=1))


class BooksQuerySchema(Schema):
    """Schema for validating book listing query parameters."""

    page = Integer(required=False, validate=validate.Range(min=1), load_default=1)
    page_size = Integer(required=False, validate=validate.Range(min=1, max=100), load_default=30)
    read = Boolean(required=False)
    search = String(required=False)
    start_with = String(required=False)
    sort_by = String(
        required=False,
        validate=validate.OneOf(
            ["title", "released", "price", "page_count", "read"],
            error="Sort field must be one of: title, released, price, page_count, read"
        ),
        load_default="title"
    )
    sort_order = String(
        required=False,
        validate=validate.OneOf(
            ["asc", "desc"],
            error="Sort order must be one of: asc, desc"
        ),
        load_default="asc"
    )
