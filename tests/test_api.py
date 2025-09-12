"""
Tests for API endpoints.
"""

import os
import unittest
import simplejson as json
from unittest.mock import patch, MagicMock
from io import BytesIO

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.datastructures import FileStorage

from librium.database import Language
from librium.database.sqlalchemy.db import Author, Base, Genre, Publisher, Series
from librium.views.api.v1 import bp as api_bp


class TestAPIBase(unittest.TestCase):
    """Base class for API tests."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Use an in-memory SQLite database for testing
        os.environ["SQLDATABASE"] = ":memory:"

    def setUp(self):
        """Set up the test client."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        # Minimal JWT config for tests
        self.app.config["JWT_SECRET_KEY"] = "dev-key-for-tests"
        self.app.config["JWT_TOKEN_LOCATION"] = ["headers"]
        self.app.config["JWT_HEADER_NAME"] = "Authorization"
        self.app.config["JWT_HEADER_TYPE"] = "Bearer"
        JWTManager(self.app)
        # Build an access token for authenticated requests
        with self.app.app_context():
            token = create_access_token(identity="test-user")
        self.auth_headers = {"Authorization": f"Bearer {token}"}
        self.app.register_blueprint(api_bp, url_prefix="/api/v1")
        self.client = self.app.test_client()


class TestAPIEndpoints(TestAPIBase):
    """Tests for API endpoints."""

    @patch("librium.views.api.v1.endpoints.SeriesService")
    def test_series(self, mock_service):
        """Test getting all series."""
        # Mock the service response
        mock_series = [Series(id=1, name="Series 1"), Series(id=2, name="Series 2")]
        mock_service.get_all.return_value = mock_series

        # Make the request
        response = self.client.get("/api/v1/series", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], "Series 1")
        self.assertEqual(data[1]["id"], 2)
        self.assertEqual(data[1]["name"], "Series 2")

    @patch("librium.views.api.v1.endpoints.GenreService")
    def test_genres(self, mock_service):
        """Test getting all genres."""
        # Mock the service response
        mock_genres = [Genre(id=1, name="Genre 1"), Genre(id=2, name="Genre 2")]
        mock_service.get_all.return_value = mock_genres

        # Make the request
        response = self.client.get("/api/v1/genres", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], "Genre 1")
        self.assertEqual(data[1]["id"], 2)
        self.assertEqual(data[1]["name"], "Genre 2")

    @patch("librium.views.api.v1.endpoints.LanguageService")
    def test_languages(self, mock_service):
        """Test getting all languages."""
        # Mock the service response
        mock_languages = [
            Language(id=1, name="Language 1"),
            Language(id=2, name="Language 2"),
        ]
        mock_service.get_all.return_value = mock_languages

        # Make the request
        response = self.client.get("/api/v1/languages", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], "Language 1")
        self.assertEqual(data[1]["id"], 2)
        self.assertEqual(data[1]["name"], "Language 2")

    @patch("librium.views.api.v1.endpoints.PublisherService")
    def test_publishers(self, mock_service):
        """Test getting all publishers."""
        # Mock the service response
        mock_publishers = [
            Publisher(id=1, name="Publisher 1"),
            Publisher(id=2, name="Publisher 2"),
        ]
        mock_service.get_all.return_value = mock_publishers

        # Make the request
        response = self.client.get("/api/v1/publishers", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], "Publisher 1")
        self.assertEqual(data[1]["id"], 2)
        self.assertEqual(data[1]["name"], "Publisher 2")

    @patch("librium.views.api.v1.endpoints.AuthorService")
    def test_add_author(self, mock_service):
        """Test adding a new author."""
        # Mock the service response
        mock_book = Author(id=1, name="Author 1")
        mock_service.create.return_value = mock_book

        # Make the request
        response = self.client.post(
            "/api/v1/add",
            json={
                "type": "author",
                "first_name": "Author",
                "last_name": "1",
            },
            headers=self.auth_headers,
        )

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Author 1")

    @patch("librium.views.api.v1.endpoints.BookService")
    def test_delete_book(self, mock_service):
        """Test deleting a book."""
        # Make the request
        response = self.client.post("/api/v1/delete", json={"type": "book", "id": 1}, headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        mock_service.delete.assert_called_once_with(1)

    @patch("librium.views.api.v1.endpoints.add_cover")
    def test_add_cover(self, mock_add_cover):
        """Test adding a cover."""
        # Mock the response
        mock_add_cover.return_value = {"success": True}

        # Create a test file
        test_file = FileStorage(
            stream=BytesIO(b"test file content"),
            filename="test.jpg",
            content_type="image/jpeg",
        )

        # Make the request
        response = self.client.post(
            "/api/v1/add/cover",
            data={"cover": test_file, "uuid": "12345678-1234-5678-1234-567812345678"},
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

    @patch("librium.views.api.v1.endpoints.export_func")
    def test_export(self, mock_export):
        """Test exporting data in different formats."""
        # Test CSV export (default)
        mock_export.return_value = "export.csv"
        response = self.client.get("/api/v1/export", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        mock_export.assert_called_with("csv")
        mock_export.reset_mock()

        # Test JSON export
        mock_export.return_value = "export.json"
        response = self.client.get("/api/v1/export?format=json", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        mock_export.assert_called_with("json")
        mock_export.reset_mock()

        # Test invalid format
        response = self.client.get("/api/v1/export?format=invalid", headers=self.auth_headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertFalse(mock_export.called)

    @patch("librium.views.api.v1.endpoints.create_backup")
    def test_backup_create(self, mock_create_backup):
        """Test creating a backup."""
        # Mock the response
        mock_create_backup.return_value = "backup.sqlite"

        # Make the request
        response = self.client.post("/api/v1/backup/create", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["filename"], "backup.sqlite")
        mock_create_backup.assert_called_once()

    @patch("librium.views.api.v1.endpoints.list_backups")
    def test_backup_list(self, mock_list_backups):
        """Test listing backups."""
        # Mock the response
        mock_backups = [
            MagicMock(filename="backup1.sqlite", size=1024, date="2023-01-01"),
            MagicMock(filename="backup2.sqlite", size=2048, date="2023-01-02"),
        ]
        mock_list_backups.return_value = mock_backups

        # Make the request
        response = self.client.get("/api/v1/backup/list", headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["filename"], "backup1.sqlite")
        self.assertEqual(data[1]["filename"], "backup2.sqlite")
        mock_list_backups.assert_called_once()

    @patch("librium.views.api.v1.endpoints.restore_from_backup")
    def test_backup_restore(self, mock_restore):
        """Test restoring from a backup."""
        # Make the request
        response = self.client.post("/api/v1/backup/restore", data={"filename": "backup.sqlite"}, headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_restore.assert_called_once_with("backup.sqlite")

    @patch("librium.views.api.v1.endpoints.delete_backup")
    def test_backup_delete(self, mock_delete):
        """Test deleting a backup."""
        # Make the request
        response = self.client.post("/api/v1/backup/delete", data={"filename": "backup.sqlite"}, headers=self.auth_headers)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_delete.assert_called_once_with("backup.sqlite")


if __name__ == "__main__":
    unittest.main()
