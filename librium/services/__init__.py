"""
Service layer for the Librium application.

This module provides services for interacting with the database models.
These services encapsulate the database operations and provide a higher-level
API for the views to use.
"""

from librium.services.authentication import AuthenticationService
from librium.services.book import BookService
from librium.services.author import AuthorService
from librium.services.publisher import PublisherService
from librium.services.format import FormatService
from librium.services.language import LanguageService
from librium.services.genre import GenreService
from librium.services.series import SeriesService
from librium.services.year import YearService

# Define __all__ to control what gets imported with "from librium.services import *"
__all__ = [
    "BookService",
    "AuthorService",
    "PublisherService",
    "FormatService",
    "LanguageService",
    "GenreService",
    "SeriesService",
    "AuthenticationService",
    "YearService",
]

