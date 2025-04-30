import os
import sys
import unittest
from decimal import Decimal
from pony.orm import db_session, select, commit

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variable for testing
os.environ["PONY_SQLDATABASE"] = ":memory:"

# Import after setting environment variable
from librium.database.pony.db import (
    Book, Author, Publisher, Format, Language, Genre, Series, 
    SeriesIndex, AuthorOrdering, db
)


class TestDatabaseModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test database in memory
        db.drop_all_tables(with_all_data=True)
        db.create_tables()

        # Create test data
        with db_session:
            # Create formats
            Format(id=1, name="Paperback")
            Format(id=2, name="Hardcover")
            Format(id=3, name="E-book")

            # Create languages
            Language(id=1, name="English")
            Language(id=2, name="Spanish")

            # Create genres
            Genre(id=1, name="Fiction")
            Genre(id=2, name="Science Fiction")
            Genre(id=3, name="Fantasy")

            # Create publishers
            Publisher(id=1, name="Publisher A")
            Publisher(id=2, name="Publisher B")

            # Create authors
            Author(id=1, first_name="John", last_name="Doe")
            Author(id=2, first_name="Jane", middle_name="M", last_name="Smith")
            Author(id=3, last_name="Johnson", suffix="Jr")

            # Create series
            Series(id=1, name="Test Series 1")
            Series(id=2, name="Test Series 2")


class TestBook(TestDatabaseModels):
    def setUp(self):
        with db_session:
            # Clean up any books from previous tests
            Book.select().delete(bulk=True)

    @db_session
    def test_create_book(self):
        # Create a new book with minimal attributes
        format1 = Format[1]  # Paperback
        book = Book(title="Test Book", format=format1)

        # Verify book was created
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.format.name, "Paperback")
        self.assertFalse(book.read)
        self.assertFalse(book.has_cover)
        self.assertIsNotNone(book.uuid)

    @db_session
    def test_create_book_with_all_attributes(self):
        # Get test data from a database
        format2 = Format[2]  # Hardcover
        lang1 = Language[1]  # English
        genre1 = Genre[1]  # Fiction
        genre2 = Genre[2]  # Science Fiction
        pub1 = Publisher[1]  # Publisher A
        author1 = Author[1]  # John Doe
        author2 = Author[2]  # Jane Smith
        series1 = Series[1]  # Test Series 1

        # Create a book with all attributes
        book = Book(
            title="Complete Book",
            isbn="9781234567890",
            released=2023,
            page_count=300,
            price=Decimal("19.99"),
            read=True,
            has_cover=True,
            format=format2
        )

        # Add relationships
        book.languages.add(lang1)
        book.genres.add(genre1)
        book.genres.add(genre2)
        book.publishers.add(pub1)

        # Add authors with ordering
        AuthorOrdering(book=book, author=author1, idx=1)
        AuthorOrdering(book=book, author=author2, idx=2)

        # Add to series
        SeriesIndex(book=book, series=series1, idx=1.0)

        # Commit changes to ensure relationships are saved
        commit()

        # Verify all attributes
        self.assertEqual(book.title, "Complete Book")
        self.assertEqual(book.isbn, "9781234567890")
        self.assertEqual(book.released, 2023)
        self.assertEqual(book.page_count, 300)
        self.assertEqual(book.price, Decimal("19.99"))
        self.assertTrue(book.read)
        self.assertTrue(book.has_cover)
        self.assertEqual(book.format.name, "Hardcover")

        # Verify relationships
        self.assertEqual(len(book.languages), 1)
        self.assertEqual(book.languages.select().first().name, "English")

        self.assertEqual(len(book.genres), 2)
        genre_names = [g.name for g in book.genres]
        self.assertIn("Fiction", genre_names)
        self.assertIn("Science Fiction", genre_names)

        self.assertEqual(len(book.publishers), 1)
        self.assertEqual(book.publishers.select().first().name, "Publisher A")

        # Verify authors and ordering
        self.assertEqual(len(book.authors), 2)
        ordered_authors = book.ordered_authors
        self.assertEqual(ordered_authors[0].first_name, "John")
        self.assertEqual(ordered_authors[1].first_name, "Jane")

        # Verify series
        self.assertEqual(len(book.series), 1)
        self.assertEqual(book.series.select().first().series.name, "Test Series 1")

    @db_session
    def test_book_properties(self):
        # Get test data from database
        format1 = Format[1]  # Paperback
        author1 = Author[1]  # John Doe
        author2 = Author[2]  # Jane Smith
        series1 = Series[1]  # Test Series 1

        # Create a book with authors and series
        book = Book(title="Property Test Book", format=format1)

        # Add authors with ordering
        AuthorOrdering(book=book, author=author1, idx=1)
        AuthorOrdering(book=book, author=author2, idx=2)

        # Add to series
        SeriesIndex(book=book, series=series1, idx=1.5)

        # Commit changes to ensure relationships are saved
        commit()

        # Test properties
        self.assertEqual(book.name, "Property Test Book")

        # Test ordered_authors property
        self.assertEqual(len(book.ordered_authors), 2)
        self.assertEqual(book.ordered_authors[0].first_name, "John")
        self.assertEqual(book.ordered_authors[1].first_name, "Jane")

        # Test author_ids property
        self.assertEqual(book.author_ids, [1, 2])

        # Test series_ids property
        self.assertEqual(book.series_ids, [1])

        # Test name setter
        book.name = "Updated Title"
        self.assertEqual(book.title, "Updated Title")

    @db_session
    def test_delete_book(self):
        # Get test data from database
        format1 = Format[1]  # Paperback

        # Create a book
        book = Book(title="Book to Delete", format=format1)
        book_id = book.id

        # Delete the book
        book.delete()

        # Verify book was deleted
        self.assertIsNone(Book.get(id=book_id))


class TestAuthor(TestDatabaseModels):
    @db_session
    def test_create_author(self):
        # Create an author with all name components
        author = Author(
            first_name="Test",
            middle_name="Middle",
            last_name="Author",
            prefix="Dr",
            suffix="PhD"
        )

        # Verify author was created with correct attributes
        self.assertEqual(author.first_name, "Test")
        self.assertEqual(author.middle_name, "Middle")
        self.assertEqual(author.last_name, "Author")
        self.assertEqual(author.prefix, "Dr")
        self.assertEqual(author.suffix, "PhD")
        self.assertIsNotNone(author.uuid)

    @db_session
    def test_author_books_properties(self):
        # Get test data from database
        format1 = Format[1]  # Paperback
        author1 = Author[1]  # John Doe
        series1 = Series[1]  # Test Series 1

        # Create books and associate with author

        # Create standalone book
        standalone_book = Book(title="Standalone Book", format=format1)
        AuthorOrdering(book=standalone_book, author=author1, idx=1)

        # Create book in series
        series_book = Book(title="Series Book", format=format1)
        AuthorOrdering(book=series_book, author=author1, idx=1)
        SeriesIndex(book=series_book, series=series1, idx=1.0)

        # Commit changes to ensure relationships are saved
        commit()

        # Test books_in_series property
        series_books = list(author1.books_in_series)
        self.assertEqual(len(series_books), 1)
        self.assertEqual(series_books[0].title, "Series Book")

        # Test books_standalone property
        standalone_books = list(author1.books_standalone)
        self.assertEqual(len(standalone_books), 1)
        self.assertEqual(standalone_books[0].title, "Standalone Book")


class TestSeries(TestDatabaseModels):
    def setUp(self):
        with db_session:
            # Clean up any books from previous tests
            Book.select().delete(bulk=True)

    @db_session
    def test_series_properties(self):
        # Get test data from database
        format1 = Format[1]  # Paperback
        series1 = Series[1]  # Test Series 1

        # Create books in series with different read statuses

        # Create read book
        read_book = Book(title="Read Book", format=format1, read=True)
        SeriesIndex(book=read_book, series=series1, idx=1.0)

        # Create unread book
        unread_book = Book(title="Unread Book", format=format1, read=False)
        SeriesIndex(book=unread_book, series=series1, idx=2.0)

        # Commit changes to ensure relationships are saved
        commit()

        # Test has_unread_books property
        self.assertTrue(series1.has_unread_books)

        # Test has_read_books property
        self.assertTrue(series1.has_read_books)

        # Test books_read property
        read_books = list(series1.books_read)
        self.assertEqual(len(read_books), 1)
        self.assertEqual(read_books[0].book.title, "Read Book")

        # Test books_unread property
        unread_books = list(series1.books_unread)
        self.assertEqual(len(unread_books), 1)
        self.assertEqual(unread_books[0].book.title, "Unread Book")


class TestSeriesIndex(TestDatabaseModels):
    @db_session
    def test_series_index_property(self):
        # Get test data from database
        format1 = Format[1]  # Paperback
        series1 = Series[1]  # Test Series 1

        # Create a book in series with integer index
        book1 = Book(title="Book with Integer Index", format=format1)
        si1 = SeriesIndex(book=book1, series=series1, idx=1.0)

        # Create a book in series with decimal index
        book2 = Book(title="Book with Decimal Index", format=format1)
        si2 = SeriesIndex(book=book2, series=series1, idx=1.5)

        # Commit changes to ensure relationships are saved
        commit()

        # Test index property for integer value
        self.assertEqual(si1.index, 1)

        # Test index property for decimal value
        self.assertEqual(si2.index, 1.5)


if __name__ == "__main__":
    unittest.main()
