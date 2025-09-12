"""
Unit tests for librium.core.utils helper functions.
These tests are isolated (no Flask app) and validate edge cases.
"""

import unittest

from librium.core.utils import (
    normalize_status,
    determine_show_status,
    get_next_status,
    parse_read_arg,
)


class TestCoreUtils(unittest.TestCase):
    def test_normalize_status(self):
        # Strings lowercased
        self.assertEqual(normalize_status("TRUE"), "true")
        self.assertEqual(normalize_status("No"), "no")
        # Numbers and bools converted to string, None -> "all"
        self.assertEqual(normalize_status(1), "1")
        self.assertEqual(normalize_status(0), "0")
        self.assertEqual(normalize_status(True), "True")  # bool is not str; str(True)
        self.assertEqual(normalize_status(False), "False")
        self.assertEqual(normalize_status(None), "all")

    def test_get_next_status_rotation(self):
        self.assertEqual(get_next_status("all"), "unread")
        self.assertEqual(get_next_status("unread"), "read")
        self.assertEqual(get_next_status("read"), "all")

    def test_parse_read_arg_rotation(self):
        # None -> interpreted as 'all' -> next is 'unread' with URL param 0
        next_status, url_param = parse_read_arg(None)
        self.assertEqual(next_status, "unread")
        self.assertEqual(url_param, 0)

        # 'unread' (0/False) -> next is 'read' with URL param 1
        next_status, url_param = parse_read_arg(0)
        self.assertEqual(next_status, "read")
        self.assertEqual(url_param, 1)

        # 'read' (1 or "true") -> next is 'all' with URL param None
        next_status, url_param = parse_read_arg(1)
        self.assertEqual(next_status, "all")
        self.assertIsNone(url_param)

        # String truthy/falsey handling
        next_status, url_param = parse_read_arg("true")
        self.assertEqual(next_status, "all")
        self.assertIsNone(url_param)
        next_status, url_param = parse_read_arg("false")
        self.assertEqual(next_status, "read")
        self.assertEqual(url_param, 1)


if __name__ == "__main__":
    unittest.main()
