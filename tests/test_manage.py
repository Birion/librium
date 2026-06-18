"""Tests for the manage blueprint routes."""

import os
import unittest

os.environ["FLASK_ENV"] = "testing"

from librium.core.app import create_app
from librium.database.sqlalchemy.db import Base, create_tables, drop_tables


class TestManageBlueprint(unittest.TestCase):
    """Test the manage blueprint routes are registered and reachable."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def test_manage_index(self):
        """The /manage/ page should return 200 and list entity types."""
        resp = self.client.get("/manage/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Manage", resp.data)
        self.assertIn(b"Authors", resp.data)
        self.assertIn(b"Genres", resp.data)
        self.assertIn(b"Series", resp.data)
        self.assertIn(b"Publishers", resp.data)
        self.assertIn(b"Formats", resp.data)
        self.assertIn(b"Languages", resp.data)

    def test_manage_entity_list_pages(self):
        """Each entity list page should return 200."""
        for entity_type in [
            "authors",
            "genres",
            "series",
            "publishers",
            "formats",
            "languages",
        ]:
            with self.subTest(entity_type=entity_type):
                resp = self.client.get(f"/manage/{entity_type}")
                self.assertEqual(resp.status_code, 200)

    def test_manage_entity_new_pages(self):
        """Each entity new page (GET) should return 200."""
        for entity_type in [
            "authors",
            "genres",
            "series",
            "publishers",
            "formats",
            "languages",
        ]:
            with self.subTest(entity_type=entity_type):
                resp = self.client.get(f"/manage/{entity_type}/new")
                self.assertEqual(resp.status_code, 200)

    def test_manage_invalid_entity_type(self):
        """An invalid entity type should return 404."""
        resp = self.client.get("/manage/invalid")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
