import os
import sys
import unittest
import json
from decimal import Decimal

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utilities
from librium.views.utilities import BookSchema, SeriesSchema, MyBoolean


class TestSchemas(unittest.TestCase):
    def test_my_boolean_field(self):
        # Test MyBoolean field with various inputs
        field = MyBoolean()

        # Test truthy values
        self.assertTrue(field.deserialize('true'))
        self.assertTrue(field.deserialize('True'))
        self.assertTrue(field.deserialize('1'))
        self.assertTrue(field.deserialize(1))
        self.assertTrue(field.deserialize(True))
        self.assertTrue(field.deserialize('on'))  # Custom truthy value

        # Test falsy values
        self.assertFalse(field.deserialize('false'))
        self.assertFalse(field.deserialize('False'))
        self.assertFalse(field.deserialize('0'))
        self.assertFalse(field.deserialize(0))
        self.assertFalse(field.deserialize(False))
        self.assertFalse(field.deserialize('off'))  # Custom falsy value

    def test_series_schema_clean(self):
        # Test SeriesSchema.clean method
        schema = SeriesSchema()

        # Test with empty idx
        data = {'series': 1, 'idx': ''}
        result = schema.load(data)
        self.assertEqual(result['idx'], 0.0)

        # Test with numeric idx
        data = {'series': 1, 'idx': '2.5'}
        result = schema.load(data)
        self.assertEqual(result['idx'], 2.5)

        # Test with extra fields (should be included due to Meta.unknown = INCLUDE)
        data = {'series': 1, 'idx': '3', 'extra': 'value'}
        result = schema.load(data)
        self.assertEqual(result['idx'], 3.0)
        self.assertEqual(result['extra'], 'value')

    def test_book_schema_parse_series(self):
        # Test BookSchema.parse_series method
        schema = BookSchema()

        # Test with series as JSON string
        data = {'title': 'Test Book', 'series': json.dumps([{'series': 1, 'idx': 2.5}])}
        result = schema.load(data)
        self.assertEqual(result['series'][0]['series'], 1)
        self.assertEqual(result['series'][0]['idx'], 2.5)

        # Test with no series
        data = {'title': 'Test Book'}
        result = schema.load(data)
        self.assertNotIn('series', result)

        # Test with empty series array
        data = {'title': 'Test Book', 'series': json.dumps([])}
        result = schema.load(data)
        self.assertEqual(result['series'], [])

    def test_book_schema_parse_isbn(self):
        # Test BookSchema.parse_isbn method
        schema = BookSchema()

        # Test with ISBN containing hyphens
        data = {'title': 'Test Book', 'isbn': '978-1-234-56789-0'}
        result = schema.load(data)
        self.assertEqual(result['isbn'], '9781234567890')

        # Test with ISBN without hyphens
        data = {'title': 'Test Book', 'isbn': '9781234567890'}
        result = schema.load(data)
        self.assertEqual(result['isbn'], '9781234567890')

        # Test with no ISBN
        data = {'title': 'Test Book'}
        result = schema.load(data)
        self.assertNotIn('isbn', result)

    def test_book_schema_full_load(self):
        # Test loading a complete book data set
        schema = BookSchema()

        # Create test data
        data = {
            'title': 'Complete Test Book',
            'isbn': '978-1-234-56789-0',
            'format': 1,
            'released': 2023,
            'price': 19.99,
            'page_count': 300,
            'read': 'on',
            'authors': '1,2',
            'genres': [1, 2],
            'publishers': '1',
            'languages': [1],
            'series': json.dumps([{'series': 1, 'idx': 1.0}]),
            'extra_field': 'should be excluded'  # Should be excluded due to Meta.unknown = EXCLUDE
        }

        # Load data
        result = schema.load(data)

        # Verify all fields were processed correctly
        self.assertEqual(result['title'], 'Complete Test Book')
        self.assertEqual(result['isbn'], '9781234567890')
        self.assertEqual(result['format'], 1)
        self.assertEqual(result['released'], 2023)
        self.assertEqual(result['price'], 19.99)
        self.assertEqual(result['page_count'], 300)
        self.assertTrue(result['read'])
        self.assertEqual(result['authors'], [1, 2])
        self.assertEqual(result['genres'], [1, 2])
        self.assertEqual(result['publishers'], [1])
        self.assertEqual(result['languages'], [1])
        self.assertEqual(result['series'][0]['series'], 1)
        self.assertEqual(result['series'][0]['idx'], 1.0)
        self.assertNotIn('extra_field', result)

    def test_book_schema_minimal_load(self):
        # Test loading minimal book data
        schema = BookSchema()

        # Create minimal test data
        data = {
            'title': 'Minimal Test Book',
            'format': 1
        }

        # Load data
        result = schema.load(data)

        # Verify required fields
        self.assertEqual(result['title'], 'Minimal Test Book')
        self.assertEqual(result['format'], 1)

        # Optional fields should not be present (except for 'read' which has a default value)
        self.assertNotIn('isbn', result)
        self.assertNotIn('released', result)
        self.assertNotIn('price', result)
        self.assertNotIn('page_count', result)
        self.assertEqual(result.get('read'), False)  # 'read' has a default value of False
        self.assertNotIn('authors', result)
        self.assertNotIn('genres', result)
        self.assertNotIn('publishers', result)
        self.assertNotIn('languages', result)
        self.assertNotIn('series', result)


if __name__ == "__main__":
    unittest.main()
