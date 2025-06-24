"""
Integration tests for critical user flows in the Librium application.
These tests verify the complete flow from HTTP request to database operation and response.
"""

import os
import unittest
from decimal import Decimal

from flask import url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from librium import create_app
from librium.database.sqlalchemy.db import (
    Base,
    Book,
    Author,
    Publisher,
    Format,
    Language,
    Genre,
    Series,
)
from librium.services.book import BookService
from librium.services.author import AuthorService
from librium.services.format import FormatService
from librium.services.publisher import PublisherService
from librium.services.genre import GenreService
from librium.services.language import LanguageService
from librium.services.series import SeriesService


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    def setUp(self):
        """Set up test environment."""
        # Configure the application for testing
        os.environ["SQLDATABASE"] = ":memory:"
        os.environ["TESTING"] = "True"
        os.environ["APPLICATION_NAME"] = "Librium Test"

        # Create the Flask application
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SERVER_NAME"] = "localhost"

        # Create a test client
        self.client = self.app.test_client()

        # Create an application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create the database and tables
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        # Create a session
        self.session = Session(engine)

        # Seed the database with test data
        self._seed_database()

    def tearDown(self):
        """Clean up after tests."""
        # Remove the application context
        self.app_context.pop()

        # Close the session
        self.session.close()

        # Reset environment variables
        os.environ.pop("SQLDATABASE", None)
        os.environ.pop("TESTING", None)
        os.environ.pop("APPLICATION_NAME", None)

    def _seed_database(self):
        """Seed the database with test data."""
        # Create test formats
        format1 = Format(name="Hardcover")
        format2 = Format(name="Paperback")
        format3 = Format(name="E-book")
        self.session.add_all([format1, format2, format3])

        # Create test languages
        language1 = Language(name="English")
        language2 = Language(name="Spanish")
        self.session.add_all([language1, language2])

        # Create test genres
        genre1 = Genre(name="Fiction")
        genre2 = Genre(name="Non-fiction")
        genre3 = Genre(name="Science Fiction")
        self.session.add_all([genre1, genre2, genre3])

        # Create test publishers
        publisher1 = Publisher(name="Test Publisher 1")
        publisher2 = Publisher(name="Test Publisher 2")
        self.session.add_all([publisher1, publisher2])

        # Create test series
        series1 = Series(name="Test Series 1")
        series2 = Series(name="Test Series 2")
        self.session.add_all([series1, series2])

        # Create test authors
        author1 = Author(name="Test Author 1")
        author2 = Author(name="Test Author 2")
        self.session.add_all([author1, author2])

        # Create test books
        book1 = Book(
            title="Test Book 1",
            format=format1,
            language=language1,
            publisher=publisher1,
            isbn="9781234567890",
            released=2020,
            page_count=200,
            price=Decimal("19.99"),
            read=True,
            has_cover=False,
        )
        book2 = Book(
            title="Test Book 2",
            format=format2,
            language=language2,
            publisher=publisher2,
            isbn="9780987654321",
            released=2021,
            page_count=300,
            price=Decimal("29.99"),
            read=False,
            has_cover=False,
        )
        self.session.add_all([book1, book2])

        # Add authors to books
        book1.authors.append(author1)
        book2.authors.append(author2)

        # Add genres to books
        book1.genres.append(genre1)
        book2.genres.append(genre2)

        # Commit the changes
        self.session.commit()


class TestBookFlows(IntegrationTestCase):
    """Tests for book-related user flows."""

    def test_view_book(self):
        """Test viewing a book's details."""
        with self.app.test_request_context():
            # Get the URL for the book view
            url = url_for("book.index", id=1)

        # Make a GET request to the book view
        response = self.client.get(url)

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the book title is in the response
        self.assertIn(b"Test Book 1", response.data)

        # Check that the book's author is in the response
        self.assertIn(b"Test Author 1", response.data)

        # Check that the book's publisher is in the response
        self.assertIn(b"Test Publisher 1", response.data)

    def test_add_book(self):
        """Test adding a new book."""
        with self.app.test_request_context():
            # Get the URL for the add book view
            url = url_for("book.add")

        # Make a POST request to add a new book
        response = self.client.post(
            url,
            data={
                "title": "New Test Book",
                "format": 3,  # E-book
                "language": 1,  # English
                "publisher": 1,  # Test Publisher 1
                "isbn": "9781122334455",
                "released": 2023,
                "page_count": 250,
                "price": "24.99",
                "read": False,
                "has_cover": False,
                "authors": [1],  # Test Author 1
                "genres": [3],  # Science Fiction
            },
            follow_redirects=True,
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the book was added to the database
        with Session(create_engine("sqlite:///:memory:")) as session:
            book = session.query(Book).filter_by(title="New Test Book").first()
            self.assertIsNotNone(book)
            self.assertEqual(book.format_id, 3)
            self.assertEqual(book.language_id, 1)
            self.assertEqual(book.publisher_id, 1)
            self.assertEqual(book.isbn, "9781122334455")
            self.assertEqual(book.released, 2023)
            self.assertEqual(book.page_count, 250)
            self.assertEqual(book.price, Decimal("24.99"))
            self.assertFalse(book.read)
            self.assertFalse(book.has_cover)

            # Check that the book has the correct author and genre
            self.assertEqual(len(book.authors), 1)
            self.assertEqual(book.authors[0].id, 1)
            self.assertEqual(len(book.genres), 1)
            self.assertEqual(book.genres[0].id, 3)

    def test_update_book(self):
        """Test updating a book's information."""
        with self.app.test_request_context():
            # Get the URL for the book view
            url = url_for("book.index", id=2)

        # Make a POST request to update the book
        response = self.client.post(
            url,
            data={
                "title": "Updated Test Book 2",
                "format": 1,  # Hardcover
                "language": 1,  # English
                "publisher": 1,  # Test Publisher 1
                "isbn": "9780987654321",
                "released": 2022,
                "page_count": 350,
                "price": "34.99",
                "read": True,
                "has_cover": True,
                "authors": [1, 2],  # Both authors
                "genres": [1, 2],  # Both genres
            },
            follow_redirects=True,
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the book was updated in the database
        with Session(create_engine("sqlite:///:memory:")) as session:
            book = session.query(Book).filter_by(id=2).first()
            self.assertIsNotNone(book)
            self.assertEqual(book.title, "Updated Test Book 2")
            self.assertEqual(book.format_id, 1)
            self.assertEqual(book.language_id, 1)
            self.assertEqual(book.publisher_id, 1)
            self.assertEqual(book.released, 2022)
            self.assertEqual(book.page_count, 350)
            self.assertEqual(book.price, Decimal("34.99"))
            self.assertTrue(book.read)
            self.assertTrue(book.has_cover)

            # Check that the book has both authors and genres
            self.assertEqual(len(book.authors), 2)
            self.assertEqual(len(book.genres), 2)


if __name__ == "__main__":
    unittest.main()
