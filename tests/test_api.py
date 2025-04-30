import os
import sys
import unittest
import json
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variable for testing
os.environ["PONY_SQLDATABASE"] = ":memory:"

# Import after setting environment variable
from librium.database.pony.db import (
    Book, Author, Publisher, Format, Language, Genre, Series, db
)
from librium import app
from pony.orm import db_session


class TestAPIEndpoints(unittest.TestCase):
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
            Format(id=1, name="Paperback")

            # Create test entities
            Series(id=1, name="Test Series")
            Genre(id=1, name="Test Genre")
            Language(id=1, name="Test Language")
            Publisher(id=1, name="Test Publisher")
            Author(id=1, first_name="Test", last_name="Author")

    def setUp(self):
        # Clean up any books from previous tests
        with db_session:
            Book.select().delete(bulk=True)

    def test_series_endpoint(self):
        response = self.client.get('/api/series')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 1)
        # Find the test series in the data
        test_series = next((s for s in data if s['name'] == 'Test Series'), None)
        self.assertIsNotNone(test_series)
        self.assertEqual(test_series['id'], 1)

    def test_genres_endpoint(self):
        response = self.client.get('/api/genres')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 1)
        # Find the test genre in the data
        test_genre = next((g for g in data if g['name'] == 'Test Genre'), None)
        self.assertIsNotNone(test_genre)
        self.assertEqual(test_genre['id'], 1)

    def test_languages_endpoint(self):
        response = self.client.get('/api/languages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 1)
        # Find the test language in the data
        test_language = next((l for l in data if l['name'] == 'Test Language'), None)
        self.assertIsNotNone(test_language)
        self.assertEqual(test_language['id'], 1)

    def test_publishers_endpoint(self):
        response = self.client.get('/api/publishers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 1)
        # Find the test publisher in the data
        test_publisher = next((p for p in data if p['name'] == 'Test Publisher'), None)
        self.assertIsNotNone(test_publisher)
        self.assertEqual(test_publisher['id'], 1)

    def test_add_endpoint_genre(self):
        response = self.client.post('/api/add', data={
            'type': 'genre',
            'name': 'New Genre'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Genre')

        # Verify genre was added to database
        with db_session:
            genre = Genre.get(name='New Genre')
            self.assertIsNotNone(genre)

    def test_add_endpoint_publisher(self):
        response = self.client.post('/api/add', data={
            'type': 'publisher',
            'name': 'New Publisher'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Publisher')

        # Verify publisher was added to database
        with db_session:
            publisher = Publisher.get(name='New Publisher')
            self.assertIsNotNone(publisher)

    def test_add_endpoint_language(self):
        response = self.client.post('/api/add', data={
            'type': 'language',
            'name': 'New Language'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Language')

        # Verify language was added to database
        with db_session:
            language = Language.get(name='New Language')
            self.assertIsNotNone(language)

    def test_add_endpoint_series(self):
        response = self.client.post('/api/add', data={
            'type': 'series',
            'name': 'New Series'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Series')

        # Verify series was added to database
        with db_session:
            series = Series.get(name='New Series')
            self.assertIsNotNone(series)

    def test_add_endpoint_author_full_name(self):
        response = self.client.post('/api/add', data={
            'type': 'author',
            'name': 'John Middle Doe'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Middle Doe')

        # Verify author was added to database with correct name parts
        with db_session:
            author = Author.get(first_name='John', middle_name='Middle', last_name='Doe')
            self.assertIsNotNone(author)

    def test_add_endpoint_author_last_name_only(self):
        response = self.client.post('/api/add', data={
            'type': 'author',
            'name': 'Smith'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Smith')

        # Verify author was added to database with only last name
        with db_session:
            author = Author.get(last_name='Smith')
            self.assertIsNotNone(author)
            self.assertEqual(author.first_name, '')
            self.assertEqual(author.middle_name, '')

    def test_add_endpoint_author_with_suffix(self):
        response = self.client.post('/api/add', data={
            'type': 'author',
            'name': 'John Doe Jr'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe Jr')

        # Verify author was added to database with suffix
        with db_session:
            author = Author.get(first_name='John', last_name='Doe', suffix='Jr')
            self.assertIsNotNone(author)

    def test_add_endpoint_missing_name(self):
        response = self.client.post('/api/add', data={
            'type': 'genre',
            'name': ''
        })
        self.assertEqual(response.status_code, 403)

    def test_add_endpoint_duplicate_name(self):
        # First add a genre
        self.client.post('/api/add', data={
            'type': 'genre',
            'name': 'Duplicate Genre'
        })

        # Try to add the same genre again
        response = self.client.post('/api/add', data={
            'type': 'genre',
            'name': 'Duplicate Genre'
        })
        self.assertEqual(response.status_code, 403)

    @patch('librium.views.api.get_directory')
    def test_delete_endpoint(self, mock_get_directory):
        # Setup mock for get_directory
        mock_dir = MagicMock()
        mock_get_directory.return_value = mock_dir

        # Create a mock cover file
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_dir.__truediv__.return_value = mock_file

        # Create a book to delete
        with db_session:
            book = Book(title="Book to Delete", format=Format[1])
            book_id = book.id

        # Delete the book
        response = self.client.post('/api/delete', data={'id': str(book_id)})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('url', data)

        # Verify book was deleted from database
        with db_session:
            self.assertIsNone(Book.get(id=book_id))

        # Verify cover file was checked and unlinked
        mock_dir.__truediv__.assert_called_once()
        mock_file.exists.assert_called_once()
        mock_file.unlink.assert_called_once()

    @patch('librium.views.api.get_directory')
    def test_add_cover_endpoint(self, mock_get_directory):
        # Setup mock for get_directory
        mock_dir = MagicMock()
        mock_get_directory.return_value = mock_dir

        # Create a mock file object
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)
        mock_dir.__truediv__.return_value = "mock_path"

        # Create a book
        with db_session:
            book = Book(title="Book with Cover", format=Format[1])
            book_uuid = book.uuid

        # Create a test image
        test_image = BytesIO(b"fake image content")

        # Add cover to the book
        with patch('builtins.open', mock_open):
            response = self.client.post(
                '/api/add/cover',
                data={
                    'uuid': book_uuid,
                    'cover': (test_image, 'test.jpg')
                },
                content_type='multipart/form-data'
            )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], 'OK')

        # Verify cover file was saved
        mock_dir.__truediv__.assert_called_with(f"{book_uuid}.jpg")
        # Check that mock_open was called with the expected arguments
        mock_open.assert_any_call("mock_path", "wb")

        # Verify book has_cover was updated
        with db_session:
            updated_book = Book.get(uuid=book_uuid)
            self.assertTrue(updated_book.has_cover)

    @patch('librium.views.api.export_func')
    def test_export_endpoint(self, mock_export_func):
        # Setup mock for export_func
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b"test,export,data")
        temp_file.close()
        mock_export_func.return_value = temp_file.name

        # Call export endpoint
        response = self.client.get('/api/export')

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename=export.csv')
        self.assertEqual(response.data, b"test,export,data")

        # Clean up temp file
        os.unlink(temp_file.name)


if __name__ == "__main__":
    unittest.main()
