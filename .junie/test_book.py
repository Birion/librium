import os
import sys
import unittest
from pony.orm import db_session, select

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variable for testing
os.environ["PONY_SQLDATABASE"] = ":memory:"

# Import after setting environment variable
from librium.database.pony.db import Book, Format, db

class TestBook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test database in memory
        db.drop_all_tables(with_all_data=True)
        db.create_tables()

        # Create a test format
        with db_session:
            Format(id=1, name="Paperback")

    @db_session
    def test_create_book(self):
        # Create a new book
        Book(title="Test Book", format=Format[1])

        # Query all books
        books = list(select(b for b in Book))

        # Verify a book was created
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Test Book")
        self.assertEqual(books[0].format.name, "Paperback")

if __name__ == "__main__":
    unittest.main()
