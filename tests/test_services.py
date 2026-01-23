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

        # Set up the mock Session facade
        mock_session.get.return_value = mock_book

        # Call the service method
        book = BookService.get_by_id(1)

        # Assert that the correct methods were called
        mock_session.get.assert_called_once_with(Book, 1)
        self.assertIsNone(book)  # Should return None for deleted books

    @patch("librium.services.book.Session")
    def test_get_by_uuid(self, mock_session):
        """Test getting a book by UUID."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.uuid = "12345678-1234-5678-1234-567812345678"

        # Mock Session.scalars(...).unique().one_or_none() chain
        mock_scalars = MagicMock()
        mock_session.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value.one_or_none.return_value = mock_book

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

        # Mock Session.scalars(...).unique().all() to return both books
        mock_scalars = MagicMock()
        mock_session.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value.all.return_value = [mock_book1, mock_book2]

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

        # Mock Session.scalars(...).unique().all() to return only non-deleted books
        mock_scalars = MagicMock()
        mock_session.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value.all.return_value = [mock_book1]

        # Call the service method
        books = BookService.get_all()

        # Verify that only the non-deleted book is returned
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertFalse(books[0].deleted)

    @patch("librium.database.sqlalchemy.transactions.Session")
    @patch("librium.services.book.Session")
    def test_create(self, mock_session, mock_tx_session):
        """Test creating a book."""
        # Mock Session.get to return a Format for the initial lookup
        mock_format = Format(name="Test Format")
        mock_format.id = 1
        mock_session.get.return_value = mock_format

        # Mock FormatService.get_by_id used inside add_or_update
        with patch(
            "librium.services.book.FormatService.get_by_id"
        ) as mock_format_service:
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
            mock_session.add.assert_called()  # book added
            mock_session.flush.assert_called_once()
            mock_format_service.assert_called_once_with(1)
            # transactional decorators may be nested; ensure at least one commit occurred
            self.assertGreaterEqual(mock_tx_session.return_value.commit.call_count, 1)

    @patch("librium.database.sqlalchemy.transactions.Session")
    @patch("librium.services.book.Session")
    def test_update(self, mock_session, mock_tx_session):
        """Test updating a book."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"

        # Mock Session.get to return the book
        mock_session.get.return_value = mock_book

        # Call the service method
        BookService.update(
            book_id=1,
            title="Updated Book",
            released=2024,
        )

        # Assert that the correct methods were called
        mock_session.get.assert_called_once_with(Book, 1)
        self.assertEqual(mock_book.title, "Updated Book")
        self.assertEqual(mock_book.released, 2024)
        # transactional decorator commits on Session() instance from transactions module
        mock_tx_session.return_value.commit.assert_called_once()

    @patch("librium.database.sqlalchemy.transactions.Session")
    @patch("librium.services.book.Session")
    def test_delete(self, mock_session, mock_tx_session):
        """Test soft deleting a book."""
        # Create a mock book
        mock_book = MagicMock(spec=Book)
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.deleted = False

        # Mock Session.get to return the book
        mock_session.get.return_value = mock_book

        # Call the service method
        result = BookService.delete(1)

        # Assert that the correct methods were called
        mock_session.get.assert_called_once_with(Book, 1)
        self.assertTrue(mock_book.deleted)  # Check that deleted flag was set to True
        self.assertTrue(result)  # Check that the method returned True
        # transactional decorator commits on Session() instance from transactions module
        mock_tx_session.return_value.commit.assert_called_once()

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

        # Mock the query to simulate filtering out deleted books
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.where.return_value = [mock_book1]  # Only the non-deleted book

        # Call the service method
        books = BookService.get_read()

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

        # Mock Session.query(...).where(...).all()
        # The actual implementation in get_unread uses list(Session.query(Book).where(...))
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        # list() on the mock_where will call __iter__
        mock_where.__iter__.return_value = iter([mock_book1])

        # Call the service method
        books = BookService.get_unread()

        # Verify that only the non-deleted book is returned
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, 1)
        self.assertEqual(books[0].title, "Test Book 1")
        self.assertFalse(books[0].read)
        self.assertFalse(books[0].deleted)

    @patch("librium.services.book.Session")
    def test_get_problems(self, mock_session):
        """Test get_problems method."""
        # Mock books for different problems
        book_no_cover = MagicMock(
            spec=Book, title="No Cover", has_cover=False, deleted=False
        )
        book_no_isbn = MagicMock(spec=Book, title="No ISBN", isbn=None, deleted=False)
        book_no_author = MagicMock(spec=Book, title="No Author", deleted=False)
        book_no_publisher = MagicMock(spec=Book, title="No Publisher", deleted=False)
        book_no_language = MagicMock(spec=Book, title="No Language", deleted=False)
        book_no_genre = MagicMock(spec=Book, title="No Genre", deleted=False)

        # We need to mock Session.scalars(...).unique().all() for each call in get_problems
        # There are 6 calls in get_problems
        mock_scalars = MagicMock()
        mock_session.scalars.return_value = mock_scalars
        mock_unique = MagicMock()
        mock_scalars.unique.return_value = mock_unique

        mock_unique.all.side_effect = [
            [book_no_cover],  # missing_cover
            [book_no_isbn],  # missing_isbn
            [book_no_author],  # missing_author
            [book_no_publisher],  # missing_publisher
            [book_no_language],  # missing_language
            [book_no_genre],  # missing_genre
        ]

        problems = BookService.get_problems()

        self.assertIn("missing_cover", problems)
        self.assertIn("missing_isbn", problems)
        self.assertIn("missing_author", problems)
        self.assertIn("missing_publisher", problems)
        self.assertIn("missing_language", problems)
        self.assertIn("missing_genre", problems)

        self.assertEqual(problems["missing_cover"], [book_no_cover])
        self.assertEqual(problems["missing_isbn"], [book_no_isbn])
        self.assertEqual(problems["missing_author"], [book_no_author])
        self.assertEqual(problems["missing_publisher"], [book_no_publisher])
        self.assertEqual(problems["missing_language"], [book_no_language])
        self.assertEqual(problems["missing_genre"], [book_no_genre])


if __name__ == "__main__":
    unittest.main()
