"""
Tests for view functions.
"""
import unittest
from unittest.mock import patch, MagicMock

from librium.views.views.utils import (
    paginate,
    apply_filters,
    apply_pagination,
    get_raw,
)
from librium.views.views.books import get_books


class TestViewUtils(unittest.TestCase):
    """Tests for view utility functions."""

    def test_paginate(self):
        """Test pagination calculation."""
        # Test with exact multiples of pagesize
        self.assertEqual(paginate(30), 1)
        self.assertEqual(paginate(60), 2)
        self.assertEqual(paginate(90), 3)

        # Test with non-exact multiples
        self.assertEqual(paginate(31), 2)
        self.assertEqual(paginate(59), 2)
        self.assertEqual(paginate(61), 3)

        # Test with zero and small values
        self.assertEqual(paginate(0), 0)
        self.assertEqual(paginate(1), 1)
        self.assertEqual(paginate(29), 1)

    def test_apply_filters(self):
        """Test applying filters to items."""
        # Create test items
        items = [
            MagicMock(name="Item 1", value=10, active=True),
            MagicMock(name="Item 2", value=20, active=False),
            MagicMock(name="Item 3", value=30, active=True),
        ]

        # Define filters
        filters = {
            "active": lambda x: x.active,
            "value_gt_15": lambda x: x.value > 15,
        }

        # Test with no arguments (no filters applied)
        result = apply_filters(filters, {}, items)
        self.assertEqual(len(result), 3)

        # Test with active filter
        result = apply_filters(filters, {"active": True}, items)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]._mock_name, "Item 1")
        self.assertEqual(result[1]._mock_name, "Item 3")

        # Test with value filter
        result = apply_filters(filters, {"value_gt_15": True}, items)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]._mock_name, "Item 2")
        self.assertEqual(result[1]._mock_name, "Item 3")

        # Test with both filters
        result = apply_filters(filters, {"active": True, "value_gt_15": True}, items)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]._mock_name, "Item 3")

    def test_apply_pagination(self):
        """Test applying pagination to items."""
        # Create test items
        items = [f"Item {i}" for i in range(1, 101)]

        # Test first page
        result = apply_pagination(1, items)
        self.assertEqual(len(result), 30)
        self.assertEqual(result[0], "Item 1")
        self.assertEqual(result[29], "Item 30")

        # Test second page
        result = apply_pagination(2, items)
        self.assertEqual(len(result), 30)
        self.assertEqual(result[0], "Item 31")
        self.assertEqual(result[29], "Item 60")

        # Test last page (partial)
        result = apply_pagination(4, items)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0], "Item 91")
        self.assertEqual(result[9], "Item 100")

        # Test page beyond available items
        result = apply_pagination(5, items)
        self.assertEqual(len(result), 0)

    @patch('librium.views.views.utils.BookService')
    def test_get_raw(self, mock_service):
        """Test getting raw items with filtering and pagination."""
        # Create mock items
        mock_items = [
            MagicMock(id=1, name="Item A", value=10),
            MagicMock(id=2, name="Item B", value=20),
            MagicMock(id=3, name="Item C", value=30),
            MagicMock(id=4, name="Item D", value=40),
            MagicMock(id=5, name="Another Item", value=50),
        ]
        mock_service.get_all.return_value = mock_items
        mock_service.get_by_id.return_value = mock_items[2]  # Item C

        # Test with no filters or pagination
        items, letters, pages = get_raw(mock_service, {}, {})
        self.assertEqual(len(items), 30)  # Default page size
        self.assertEqual(len(letters), 2)  # 'a', 'i'
        self.assertEqual(pages, 1)

        # Test with filters
        filters = {
            "value_gt_20": lambda x: x.value > 20,
        }
        items, letters, pages = get_raw(mock_service, {}, filters)
        self.assertEqual(len(items), 3)  # Items C, D, Another Item
        self.assertEqual(pages, 1)

        # Test with pagination
        items, letters, pages = get_raw(mock_service, {"page": 2}, {})
        self.assertEqual(len(items), 0)  # No items on page 2
        self.assertEqual(pages, 1)

        # Test with direct ID lookup
        items, letters, pages = get_raw(mock_service, {"id": 3}, {})
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 3)
        self.assertEqual(pages, 1)


class TestBookViews(unittest.TestCase):
    """Tests for book view functions."""

    @patch('librium.views.views.books.get_raw')
    def test_get_books(self, mock_get_raw):
        """Test getting books with various filters."""
        # Mock the get_raw function
        mock_get_raw.return_value = (
            [MagicMock(title="Book 1"), MagicMock(title="Book 2")],  # books
            ['b'],  # letters
            1,  # pages
        )

        # Test with no arguments
        result = get_books({})
        self.assertEqual(len(result["books"]), 2)
        self.assertEqual(result["letters"], ['b'])
        self.assertEqual(result["pagination"], 1)

        # Test with start argument
        result = get_books({"start": "B"})
        self.assertEqual(len(result["books"]), 2)
        # Verify that the correct filter was created
        filters = mock_get_raw.call_args[0][2]
        self.assertIn("start", filters)

        # Test with name argument
        result = get_books({"name": "Book 1"})
        self.assertEqual(len(result["books"]), 2)
        # Verify that the correct filter was created
        filters = mock_get_raw.call_args[0][2]
        self.assertIn("name", filters)

        # Test with read argument
        result = get_books({"read": True})
        self.assertEqual(len(result["books"]), 2)
        # Verify that the correct filter was created
        filters = mock_get_raw.call_args[0][2]
        self.assertIn("read", filters)

        # Test with search argument
        result = get_books({"search": "Book"})
        self.assertEqual(len(result["books"]), 2)
        # Verify that the correct filter was created
        filters = mock_get_raw.call_args[0][2]
        self.assertIn("search", filters)


if __name__ == "__main__":
    unittest.main()