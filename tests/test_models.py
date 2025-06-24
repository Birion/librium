"""
Tests for database models.
"""

import os
import unittest
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from librium.database.sqlalchemy.db import (
    Base,
    Book,
    Author,
    Publisher,
    Format,
    Language,
    Genre,
    Series,
    SeriesIndex,
    AuthorOrdering,
    create_tables,
)


class TestBase(unittest.TestCase):
    """Base class for model tests."""

    @classmethod
    def setUpClass(cls):
        """Set up the test database."""
        # Use an in-memory SQLite database for testing
        os.environ["SQLDATABASE"] = ":memory:"
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)

    def setUp(self):
        """Set up a new session for each test."""
        self.session = Session(self.engine)

    def tearDown(self):
        """Clean up after each test."""
        self.session.rollback()
        self.session.close()


class TestBook(TestBase):
    """Tests for the Book model."""

    def test_create_book(self):
        """Test creating a book."""
        # Create a format first (required for book)
        format_obj = Format(name="Hardcover")
        self.session.add(format_obj)
        self.session.commit()

        # Create a book
        book = Book(
            title="Test Book",
            isbn="9781234567897",  # Valid ISBN-13
            released=2023,
            page_count=200,
            price=Decimal("19.99"),
            read=False,
            has_cover=False,
            format_id=format_obj.id,
            uuid="12345678-1234-5678-1234-567812345678",
        )
        self.session.add(book)
        self.session.commit()

        # Retrieve the book from the database
        retrieved_book = self.session.query(Book).filter_by(title="Test Book").first()

        # Assert that the book was created correctly
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.title, "Test Book")
        self.assertEqual(retrieved_book.isbn, "9781234567897")
        self.assertEqual(retrieved_book.released, 2023)
        self.assertEqual(retrieved_book.page_count, 200)
        self.assertEqual(retrieved_book.price, Decimal("19.99"))
        self.assertFalse(retrieved_book.read)
        self.assertFalse(retrieved_book.has_cover)
        self.assertEqual(retrieved_book.format_id, format_obj.id)
        self.assertEqual(retrieved_book.uuid, "12345678-1234-5678-1234-567812345678")

    def test_book_properties(self):
        """Test book properties."""
        # Create a format first (required for book)
        format_obj = Format(name="Paperback")
        self.session.add(format_obj)
        self.session.commit()

        # Create a book
        book = Book(
            title="Property Test Book",
            format_id=format_obj.id,
            uuid="12345678-1234-5678-1234-567812345678",
        )
        self.session.add(book)
        self.session.commit()

        # Test name property
        self.assertEqual(book.name, "Property Test Book")

        # Test name setter
        book.name = "Updated Title"
        self.assertEqual(book.title, "Updated Title")

        # Test hex_uuid property
        self.assertEqual(book.hex_uuid, "12345678123456781234567812345678")

    def test_book_relationships(self):
        """Test book relationships."""
        # Create required objects
        format_obj = Format(name="E-book")
        self.session.add(format_obj)

        author1 = Author(name="Author One")
        author2 = Author(name="Author Two")
        self.session.add_all([author1, author2])

        publisher = Publisher(name="Test Publisher")
        self.session.add(publisher)

        language = Language(name="English")
        self.session.add(language)

        genre = Genre(name="Fiction")
        self.session.add(genre)

        series = Series(name="Test Series")
        self.session.add(series)

        self.session.commit()

        # Create a book
        book = Book(
            title="Relationship Test Book",
            format_id=format_obj.id,
            uuid="12345678-1234-5678-1234-567812345678",
        )
        self.session.add(book)
        self.session.commit()

        # Add relationships
        author_ordering1 = AuthorOrdering(book=book, author=author1, idx=1)
        author_ordering2 = AuthorOrdering(book=book, author=author2, idx=2)
        self.session.add_all([author_ordering1, author_ordering2])

        book.publishers.append(publisher)
        book.languages.append(language)
        book.genres.append(genre)

        series_index = SeriesIndex(book=book, series=series, idx=1)
        self.session.add(series_index)

        self.session.commit()

        # Test relationships
        self.assertEqual(len(book.authors), 2)
        self.assertEqual(book.ordered_authors[0].name, "Author One")
        self.assertEqual(book.ordered_authors[1].name, "Author Two")
        self.assertEqual(book.author_ids, [author1.id, author2.id])

        self.assertEqual(len(book.publishers), 1)
        self.assertEqual(book.publishers[0].name, "Test Publisher")
        self.assertEqual(book.publisher_ids, [publisher.id])

        self.assertEqual(len(book.languages), 1)
        self.assertEqual(book.languages[0].name, "English")
        self.assertEqual(book.language_ids, [language.id])

        self.assertEqual(len(book.genres), 1)
        self.assertEqual(book.genres[0].name, "Fiction")
        self.assertEqual(book.genre_ids, [genre.id])

        self.assertEqual(len(book.series), 1)
        self.assertEqual(book.series[0].series.name, "Test Series")
        self.assertEqual(book.series_ids, [series.id])

    def test_validate_isbn(self):
        """Test ISBN validation."""
        # Valid ISBN-13
        self.assertTrue(Book.validate_isbn("9781234567897"))
        # Invalid ISBN-13 (wrong checksum)
        self.assertFalse(Book.validate_isbn("9781234567890"))
        # Invalid ISBN-13 (wrong length)
        self.assertFalse(Book.validate_isbn("978123456789"))
        # Invalid ISBN-13 (contains non-digits)
        self.assertFalse(Book.validate_isbn("978123456789X"))
        # None is valid (optional field)
        self.assertTrue(Book.validate_isbn(None))


class TestAuthor(TestBase):
    """Tests for the Author model."""

    def test_create_author(self):
        """Test creating an author."""
        author = Author(name="Test Author")
        self.session.add(author)
        self.session.commit()

        retrieved_author = (
            self.session.query(Author).filter_by(name="Test Author").first()
        )
        self.assertIsNotNone(retrieved_author)
        self.assertEqual(retrieved_author.name, "Test Author")

    def test_author_validation(self):
        """Test author validation."""
        # Name is required
        with self.assertRaises(Exception):
            author = Author()
            self.session.add(author)
            self.session.commit()

        # Name must be between 1 and 100 characters
        with self.assertRaises(Exception):
            author = Author(name="A" * 101)
            self.session.add(author)
            self.session.commit()


if __name__ == "__main__":
    unittest.main()
