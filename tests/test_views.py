import os
import sys
import unittest
import json
from unittest.mock import patch

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variable for testing
os.environ["PONY_SQLDATABASE"] = ":memory:"

# Import after setting environment variable
from librium.database.pony.db import (
    Book, Author, Publisher, Format, Language, Genre, Series, 
    SeriesIndex, AuthorOrdering, db
)
from librium import app
from pony.orm import db_session


class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test database in memory
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        
        # Configure Flask app for testing
        app.config['TESTING'] = True
        cls.client = app.test_client()
        
        # Create test data
        with db_session:
            # Create formats
            cls.format1 = Format(id=1, name="Paperback")
            cls.format2 = Format(id=2, name="Hardcover")
            
            # Create languages
            cls.lang1 = Language(id=1, name="English")
            cls.lang2 = Language(id=2, name="Spanish")
            
            # Create genres
            cls.genre1 = Genre(id=1, name="Fiction")
            cls.genre2 = Genre(id=2, name="Science Fiction")
            
            # Create publishers
            cls.pub1 = Publisher(id=1, name="Publisher A")
            cls.pub2 = Publisher(id=2, name="Publisher B")
            
            # Create authors
            cls.author1 = Author(id=1, first_name="John", last_name="Doe")
            cls.author2 = Author(id=2, first_name="Jane", last_name="Smith")
            
            # Create series
            cls.series1 = Series(id=1, name="Test Series 1")
            cls.series2 = Series(id=2, name="Test Series 2")
    
    def setUp(self):
        # Clean up any books from previous tests
        with db_session:
            Book.select().delete(bulk=True)


class TestBookViews(TestViews):
    def test_book_index_get_nonexistent(self):
        # Test GET request for a book that doesn't exist
        response = self.client.get('/book/999')
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(response.headers['Location'], '/')
    
    def test_book_index_get_existing(self):
        # Create a book
        with db_session:
            book = Book(title="Test Book", format=self.format1)
            book_id = book.id
        
        # Test GET request for an existing book
        response = self.client.get(f'/book/{book_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)
    
    def test_book_index_post(self):
        # Create a book to update
        with db_session:
            book = Book(title="Book to Update", format=self.format1)
            book_id = book.id
        
        # Update the book
        response = self.client.post(
            f'/book/{book_id}',
            data={
                'title': 'Updated Book Title',
                'format': 2,  # Hardcover
                'authors': [1, 2],  # John Doe and Jane Smith
                'genres': [1, 2],  # Fiction and Science Fiction
                'publishers': [1],  # Publisher A
                'languages': [1],  # English
                'series': json.dumps([{'series': 1, 'idx': 1.0}])  # Test Series 1
            },
            follow_redirects=False
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['url'], f'/book/{book_id}')
        
        # Verify book was updated in database
        with db_session:
            updated_book = Book[book_id]
            self.assertEqual(updated_book.title, 'Updated Book Title')
            self.assertEqual(updated_book.format.id, 2)
            
            # Check relationships
            self.assertEqual(len(updated_book.authors), 2)
            self.assertEqual(len(updated_book.genres), 2)
            self.assertEqual(len(updated_book.publishers), 1)
            self.assertEqual(len(updated_book.languages), 1)
            self.assertEqual(len(updated_book.series), 1)
            
            # Check author ordering
            authors = updated_book.ordered_authors
            self.assertEqual(authors[0].first_name, 'John')
            self.assertEqual(authors[1].first_name, 'Jane')
            
            # Check series index
            series_index = updated_book.series.select().first()
            self.assertEqual(series_index.series.id, 1)
            self.assertEqual(series_index.idx, 1.0)
    
    def test_book_add_get(self):
        # Test GET request for add book page
        response = self.client.get('/book/add')
        self.assertEqual(response.status_code, 200)
        
        # Check that the page contains form elements
        self.assertIn(b'<form', response.data)
        self.assertIn(b'name="title"', response.data)
    
    def test_book_add_post(self):
        # Add a new book
        response = self.client.post(
            '/book/add',
            data={
                'title': 'New Book',
                'isbn': '9781234567890',
                'format': 1,  # Paperback
                'released': 2023,
                'price': 19.99,
                'page_count': 300,
                'read': 'on',  # true
                'authors': [1],  # John Doe
                'genres': [1],  # Fiction
                'publishers': [1],  # Publisher A
                'languages': [1],  # English
                'series': json.dumps([])  # No series
            },
            follow_redirects=False
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('/book/', data['url'])
        
        # Extract book ID from URL
        book_id = int(data['url'].split('/')[-1])
        
        # Verify book was created in database
        with db_session:
            new_book = Book[book_id]
            self.assertEqual(new_book.title, 'New Book')
            self.assertEqual(new_book.isbn, '9781234567890')
            self.assertEqual(new_book.format.id, 1)
            self.assertEqual(new_book.released, 2023)
            self.assertEqual(float(new_book.price), 19.99)
            self.assertEqual(new_book.page_count, 300)
            self.assertTrue(new_book.read)
            
            # Check relationships
            self.assertEqual(len(new_book.authors), 1)
            self.assertEqual(new_book.ordered_authors[0].first_name, 'John')
            self.assertEqual(len(new_book.genres), 1)
            self.assertEqual(new_book.genres.select().first().name, 'Fiction')
            self.assertEqual(len(new_book.publishers), 1)
            self.assertEqual(new_book.publishers.select().first().name, 'Publisher A')
            self.assertEqual(len(new_book.languages), 1)
            self.assertEqual(new_book.languages.select().first().name, 'English')
            self.assertEqual(len(new_book.series), 0)
    
    def test_book_add_with_series(self):
        # Add a new book with series
        response = self.client.post(
            '/book/add',
            data={
                'title': 'Book in Series',
                'format': 1,  # Paperback
                'authors': [1],  # John Doe
                'series': json.dumps([{'series': 1, 'idx': 2.5}])  # Test Series 1, index 2.5
            },
            follow_redirects=False
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        book_id = int(data['url'].split('/')[-1])
        
        # Verify book was created with series
        with db_session:
            new_book = Book[book_id]
            self.assertEqual(new_book.title, 'Book in Series')
            
            # Check series
            self.assertEqual(len(new_book.series), 1)
            series_index = new_book.series.select().first()
            self.assertEqual(series_index.series.id, 1)
            self.assertEqual(series_index.idx, 2.5)
            self.assertEqual(series_index.index, 2.5)  # Test index property


class TestMainViews(TestViews):
    def test_main_index(self):
        # Create some books
        with db_session:
            # Create a read book
            Book(title="Read Book", format=self.format1, read=True)
            
            # Create an unread book
            Book(title="Unread Book", format=self.format1, read=False)
        
        # Test GET request for main index
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check that both books are listed
        self.assertIn(b'Read Book', response.data)
        self.assertIn(b'Unread Book', response.data)


if __name__ == "__main__":
    unittest.main()