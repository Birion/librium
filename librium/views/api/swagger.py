"""
Swagger documentation for the Librium API.

This module provides Swagger/OpenAPI documentation for the Librium API endpoints.
"""

from flask_swagger_ui import get_swaggerui_blueprint

# Define Swagger UI blueprint
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI
API_URL = "/api/swagger.json"  # URL for the Swagger JSON documentation

# Create Swagger UI blueprint
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Librium API Documentation"}
)

# Swagger specification
swagger_spec = {
    "swagger": "2.0",
    "info": {
        "title": "Librium API",
        "description": "API for the Librium book management system",
        "version": "1.0",
    },
    "basePath": "/api/v1",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
        }
    },
    "security": [{"Bearer": []}],
    "paths": {
        "/books": {
            "get": {
                "tags": ["Data Retrieval"],
                "summary": "Get books with filtering and sorting",
                "description": "Returns a list of books with filtering and sorting options",
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "description": "Page number",
                        "required": False,
                        "type": "integer",
                        "default": 1,
                    },
                    {
                        "name": "page_size",
                        "in": "query",
                        "description": "Number of items per page",
                        "required": False,
                        "type": "integer",
                        "default": 30,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    {
                        "name": "read",
                        "in": "query",
                        "description": "Filter by read status",
                        "required": False,
                        "type": "boolean",
                    },
                    {
                        "name": "search",
                        "in": "query",
                        "description": "Search term for book title",
                        "required": False,
                        "type": "string",
                    },
                    {
                        "name": "start_with",
                        "in": "query",
                        "description": "Filter books by title starting with this string",
                        "required": False,
                        "type": "string",
                    },
                    {
                        "name": "sort_by",
                        "in": "query",
                        "description": "Field to sort by",
                        "required": False,
                        "type": "string",
                        "enum": ["title", "released", "price", "page_count", "read"],
                        "default": "title",
                    },
                    {
                        "name": "sort_order",
                        "in": "query",
                        "description": "Sort order",
                        "required": False,
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "default": "asc",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "books": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "uuid": {"type": "string"},
                                            "isbn": {"type": "string"},
                                            "released": {"type": "integer"},
                                            "price": {"type": "number"},
                                            "page_count": {"type": "integer"},
                                            "read": {"type": "boolean"},
                                            "has_cover": {"type": "boolean"},
                                            "format": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                },
                                            },
                                            "authors": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                    },
                                                },
                                            },
                                            "genres": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                    },
                                                },
                                            },
                                            "publishers": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                    },
                                                },
                                            },
                                            "languages": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                    },
                                                },
                                            },
                                            "series": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                        "index": {"type": "number"},
                                                    },
                                                },
                                            },
                                            "created_at": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                            "updated_at": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                        },
                                    },
                                },
                                "pagination": {
                                    "type": "object",
                                    "properties": {
                                        "page": {"type": "integer"},
                                        "page_size": {"type": "integer"},
                                        "total_items": {"type": "integer"},
                                        "total_pages": {"type": "integer"},
                                    },
                                },
                                "filters": {
                                    "type": "object",
                                    "properties": {
                                        "read": {"type": "boolean"},
                                        "search": {"type": "string"},
                                        "start_with": {"type": "string"},
                                    },
                                },
                                "sorting": {
                                    "type": "object",
                                    "properties": {
                                        "sort_by": {"type": "string"},
                                        "sort_order": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Internal server error"},
                },
            }
        },
        "/series": {
            "get": {
                "tags": ["Data Retrieval"],
                "summary": "Get all series",
                "description": "Returns a list of all series in the system",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/genres": {
            "get": {
                "tags": ["Data Retrieval"],
                "summary": "Get all genres",
                "description": "Returns a list of all genres in the system",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/languages": {
            "get": {
                "tags": ["Data Retrieval"],
                "summary": "Get all languages",
                "description": "Returns a list of all languages in the system",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/publishers": {
            "get": {
                "tags": ["Data Retrieval"],
                "summary": "Get all publishers",
                "description": "Returns a list of all publishers in the system",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/add": {
            "post": {
                "tags": ["Data Modification"],
                "summary": "Add a new entity",
                "description": "Add a new entity (genre, publisher, language, series, author)",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "type",
                        "in": "formData",
                        "description": "Type of entity to add",
                        "required": True,
                        "type": "string",
                        "enum": ["genre", "publisher", "language", "series", "author"],
                    },
                    {
                        "name": "name",
                        "in": "formData",
                        "description": "Name of the entity",
                        "required": True,
                        "type": "string",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Entity created successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Object already exists or missing name"},
                },
            }
        },
        "/delete": {
            "post": {
                "tags": ["Data Modification"],
                "summary": "Delete a book",
                "description": "Delete a book by ID",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "id",
                        "in": "formData",
                        "description": "ID of the book to delete",
                        "required": True,
                        "type": "integer",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Book deleted successfully",
                        "schema": {
                            "type": "object",
                            "properties": {"url": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/add/cover": {
            "post": {
                "tags": ["Data Modification"],
                "summary": "Add a cover image for a book",
                "description": "Upload a cover image for a book identified by UUID",
                "consumes": ["multipart/form-data"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "cover",
                        "in": "formData",
                        "description": "Cover image file",
                        "required": True,
                        "type": "file",
                    },
                    {
                        "name": "uuid",
                        "in": "formData",
                        "description": "UUID of the book",
                        "required": True,
                        "type": "string",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Cover uploaded successfully",
                        "schema": {
                            "type": "object",
                            "properties": {"response": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Book not found"},
                    "500": {"description": "Failed to save cover"},
                },
            }
        },
        "/export": {
            "get": {
                "tags": ["Data Export"],
                "summary": "Export books",
                "description": "Export books to the specified format (CSV or JSON)",
                "produces": ["text/csv", "application/json"],
                "parameters": [
                    {
                        "name": "format",
                        "in": "query",
                        "description": "Export format",
                        "required": False,
                        "type": "string",
                        "enum": ["csv", "json"],
                        "default": "csv",
                    }
                ],
                "responses": {
                    "200": {"description": "File download"},
                    "400": {"description": "Invalid format"},
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Failed to export books"},
                },
            }
        },
        "/backup/create": {
            "post": {
                "tags": ["Backup"],
                "summary": "Create a backup",
                "description": "Create a backup of the database",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "filename",
                        "in": "formData",
                        "description": "Optional name for the backup file",
                        "required": False,
                        "type": "string",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Backup created successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                                "filename": {"type": "string"},
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Error creating backup"},
                },
            }
        },
        "/backup/list": {
            "get": {
                "tags": ["Backup"],
                "summary": "List backups",
                "description": "List all available backups",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "List of backups",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "backups": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "filename": {"type": "string"},
                                            "path": {"type": "string"},
                                            "size": {"type": "integer"},
                                            "created": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Error listing backups"},
                },
            }
        },
        "/backup/restore": {
            "post": {
                "tags": ["Backup"],
                "summary": "Restore from backup",
                "description": "Restore the database from a backup",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "filename",
                        "in": "formData",
                        "description": "Backup file name or special keywords (latest, last, first)",
                        "required": True,
                        "type": "string",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Database restored successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Backup file not found"},
                    "500": {"description": "Error restoring database"},
                },
            }
        },
        "/backup/delete": {
            "post": {
                "tags": ["Backup"],
                "summary": "Delete backup",
                "description": "Delete a backup file",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "filename",
                        "in": "formData",
                        "description": "Backup file name to delete",
                        "required": True,
                        "type": "string",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Backup deleted successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Backup file not found"},
                    "500": {"description": "Error deleting backup"},
                },
            }
        },
        "/auth/token": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Get authentication token",
                "description": "Get JWT token for API authentication",
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "name": "username",
                        "in": "formData",
                        "description": "Username",
                        "required": True,
                        "type": "string",
                    },
                    {
                        "name": "password",
                        "in": "formData",
                        "description": "Password",
                        "required": True,
                        "type": "string",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Authentication successful",
                        "schema": {
                            "type": "object",
                            "properties": {"access_token": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Bad username or password"},
                },
            }
        },
        "/protected": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Test authentication",
                "description": "Test if the authentication token is valid",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Authentication successful",
                        "schema": {
                            "type": "object",
                            "properties": {"msg": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
    },
}
