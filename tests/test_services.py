"""
Tests for service layer.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
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
)
from librium.services.book import BookService
from librium.services.author import AuthorService
from librium.services.format import FormatService


class TestServiceBase(unittest.TestCase):
    """Base class for service tests."""

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
        # Create a format for testing
        self.format = Format(name="Test Format")
        self.session.add(self.format)
        self.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        self.session.rollback()
        self.session.close()


class TestBookService(TestServiceBase):
    """Tests for the BookService."""

    @patch("librium.services.book.Session")
    def test_get_by_id(self, mock_session):
        """Test getting a book by ID."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.deleted = False

        # Set up the mock session (module-level Session API)
        mock_session.get.return_value = mock_book

        # Call the service method
        book = BookService.get_by_id(1)

        # Assert that the correct methods were called
        mock_session.get.assert_called_once_with(Book, 1)
        self.assertEqual(book.id, 1)
        self.assertEqual(book.title, "Test Book")

    @patch("librium.services.book.Session")
    def test_get_by_id_deleted(self, mock_session):
        """Test getting a deleted book by ID returns None."""
        # Create a mock book that is deleted
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.deleted = True

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.get.return_value = mock_book

        # Call the service method
        book = BookService.get_by_id(1)

        # Assert that the correct methods were called
        mock_session_instance.get.assert_called_once_with(Book, 1)
        self.assertIsNone(book)  # Should return None for deleted books

    @patch("librium.services.book.Session")
    def test_get_by_uuid(self, mock_session):
        """Test getting a book by UUID."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.uuid = "12345678-1234-5678-1234-567812345678"

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.execute.return_value.scalar_one_or_none.return_value = (
            mock_book
        )

        # Call the service method
        book = BookService.get_by_uuid("12345678-1234-5678-1234-567812345678")

        # Assert that the correct methods were called
        self.assertEqual(book.id, 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.uuid, "12345678-1234-5678-1234-567812345678")

    @patch("librium.services.book.Session")
    def test_get_all(self, mock_session):
        """Test getting all non-deleted books."""
        # Create mock books
        mock_book1 = MagicMock(spec=Book)
        mock_book1.id = 1
        mock_book1.title = "Test Book 1"
        mock_book1.deleted = False

        mock_book2 = MagicMock(spec=Book)
        mock_book2.id = 2
        mock_book2.title = "Test Book 2"
        mock_book2.deleted = False

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter.return_value = [
            mock_book1,
            mock_book2,
        ]

        # Call the service method
        books = BookService.get_all()

        # Assert that the correct methods were called
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertEqual(books[1].id, 2)
        self.assertEqual(books[1].title, "Test Book 2")

    @patch("librium.services.book.Session")
    def test_get_all_excludes_deleted(self, mock_session):
        """Test that get_all excludes deleted books."""
        # Create mock books - one deleted, one not
        mock_book1 = MagicMock(spec=Book)
        mock_book1.id = 1
        mock_book1.title = "Test Book 1"
        mock_book1.deleted = False

        mock_book2 = MagicMock(spec=Book)
        mock_book2.id = 2
        mock_book2.title = "Test Book 2"
        mock_book2.deleted = True  # This book is deleted

        # Set up the mock session to return both books when queried
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        # Mock the filter to simulate filtering out deleted books
        mock_query = MagicMock()
        mock_session_instance.query.return_value = mock_query
        mock_query.filter.return_value = [mock_book1]  # Only the non-deleted book

        # Call the service method
        books = BookService.get_all()

        # Assert that the correct methods were called
        mock_session_instance.query.assert_called_once_with(Book)
        mock_query.filter.assert_called_once()

        # Verify that only the non-deleted book is returned
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertFalse(books[0].deleted)

    @patch("librium.services.book.Session")
    def test_create(self, mock_session):
        """Test creating a book."""
        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        # Mock the format service
        with patch(
            "librium.services.book.FormatService.get_by_id"
        ) as mock_format_service:
            mock_format = MagicMock(spec=Format)
            mock_format.id = 1
            mock_format.name = "Test Format"
            mock_format_service.return_value = mock_format

            # Call the service method
            BookService.create(
                title="New Book",
                format_id=1,
                isbn="9781234567897",
                released=2023,
                page_count=200,
                price=Decimal("19.99"),
                read=False,
                has_cover=False,
            )

            # Assert that the correct methods were called
            mock_format_service.assert_called_once_with(1)
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()

    @patch("librium.services.book.Session")
    def test_update(self, mock_session):
        """Test updating a book."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.get.return_value = mock_book

        # Call the service method
        BookService.update(
            book_id=1,
            title="Updated Book",
            released=2024,
        )

        # Assert that the correct methods were called
        mock_session_instance.get.assert_called_once_with(Book, 1)
        self.assertEqual(mock_book.title, "Updated Book")
        self.assertEqual(mock_book.released, 2024)
        mock_session_instance.commit.assert_called_once()

    @patch("librium.services.book.Session")
    def test_delete(self, mock_session):
        """Test soft deleting a book."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.deleted = False

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.get.return_value = mock_book

        # Call the service method
        result = BookService.delete(1)

        # Assert that the correct methods were called
        mock_session_instance.get.assert_called_once_with(Book, 1)
        self.assertTrue(mock_book.deleted)  # Check that deleted flag was set to True
        self.assertTrue(result)  # Check that the method returned True
        mock_session_instance.commit.assert_called_once()

    @patch("librium.services.book.Session")
    def test_get_read_excludes_deleted(self, mock_session):
        """Test that get_read excludes deleted books."""
        # Create mock books - one deleted and read, one not deleted and read
        mock_book1 = MagicMock(spec=Book)
        mock_book1.id = 1
        mock_book1.title = "Test Book 1"
        mock_book1.read = True
        mock_book1.deleted = False

        mock_book2 = MagicMock(spec=Book)
        mock_book2.id = 2
        mock_book2.title = "Test Book 2"
        mock_book2.read = True
        mock_book2.deleted = True  # This book is deleted

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        # Mock the query to simulate filtering out deleted books
        mock_query = MagicMock()
        mock_session_instance.query.return_value = mock_query
        mock_query.where.return_value = [mock_book1]  # Only the non-deleted book

        # Call the service method
        books = BookService.get_read()

        # Assert that the correct methods were called
        mock_session_instance.query.assert_called_once_with(Book)
        mock_query.where.assert_called_once()

        # Verify that only the non-deleted book is returned
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertTrue(books[0].read)
        self.assertFalse(books[0].deleted)

    @patch("librium.services.book.Session")
    def test_get_unread_excludes_deleted(self, mock_session):
        """Test that get_unread excludes deleted books."""
        # Create mock books - one deleted and unread, one not deleted and unread
        mock_book1 = MagicMock(spec=Book)
        mock_book1.id = 1
        mock_book1.title = "Test Book 1"
        mock_book1.read = False
        mock_book1.deleted = False

        mock_book2 = MagicMock(spec=Book)
        mock_book2.id = 2
        mock_book2.title = "Test Book 2"
        mock_book2.read = False
        mock_book2.deleted = True  # This book is deleted

        # Set up the mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        # Mock the query to simulate filtering out deleted books
        mock_query = MagicMock()
        mock_session_instance.query.return_value = mock_query
        mock_query.where.return_value = [mock_book1]  # Only the non-deleted book

        # Call the service method
        books = BookService.get_unread()

        # Assert that the correct methods were called
        mock_session_instance.query.assert_called_once_with(Book)
        mock_query.where.assert_called_once()

        # Verify that only the non-deleted book is returned
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertFalse(books[0].read)
        self.assertFalse(books[0].deleted)


if __name__ == "__main__":
    unittest.main()
