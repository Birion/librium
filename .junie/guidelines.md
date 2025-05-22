# Librium Development Guidelines

This document provides essential information for developers working on the Librium project.

## Build/Configuration Instructions

### Environment Setup

1. **Python Version**: Librium requires Python 3.11.

2. **Dependencies Management**: This project uses Pipenv for dependency management.
   ```bash
   # Install pipenv if you don't have it
   pip install pipenv
   
   # Install dependencies
   pipenv install
   
   # Activate the virtual environment
   pipenv shell
   ```

3. **Environment Variables**: Create a `.env` file in the project root with the following variables:
   ```
   PONY_SQLDATABASE=librium.sqlite  # Path to the SQLite database file
   APPLICATION_NAME=Librium         # Application name for display
   ```

### Running the Application

1. **Development Server**:
   ```bash
   # Run the Flask development server
   python -m flask --app librium:app run --debug
   ```

2. **Production Deployment**:
   The project includes a `uwsgi.ini` file for deployment with uWSGI. Adjust the paths in this file to match your environment.
   ```bash
   uwsgi --ini uwsgi.ini
   ```

## Testing Information

### Test Configuration

1. **Test Database**: Tests should use an in-memory SQLite database to avoid affecting the production database.
   ```python
   import os
   
   os.environ["PONY_SQLDATABASE"] = ":memory:"
   ```

2. **Test Structure**: Tests should be organized by module and functionality. Use Python's unittest framework.

### Running Tests

1. **Running Individual Tests**:
   ```bash
   python path/to/test_file.py
   ```

2. **Running All Tests**:
   ```bash
   python -m unittest discover -s tests
   ```

### Adding New Tests

1. **Test File Naming**: Name test files with the prefix `test_` followed by the name of the module being tested.

2. **Test Class Structure**: Each test file should contain one or more test classes that inherit from `unittest.TestCase`.

3. **Database Tests**: When testing database operations, use the `@db_session` decorator and create an in-memory database.

### Example Test

Here's a simple test for the Book model:

```python
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
        # Create a test database in memory
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
```

## Additional Development Information

### Project Structure

- **librium/core/**: Core application components
- **librium/database/**: Database models and configuration
- **librium/static/**: Static assets (CSS, JavaScript, images)
- **librium/templates/**: Jinja2 templates
- **librium/views/**: Flask blueprints and view functions

### Database ORM

Librium uses Pony ORM for database operations. Key points:

1. **Entity Definitions**: Database models are defined in `librium/database/pony/db.py`.

2. **Database Sessions**: Use the `@db_session` decorator for functions that interact with the database.

3. **Queries**: Use Pony's query language for database operations:
   ```python
   from librium.database.pony.db import Book, select
   
   # Get a book by ID
   book = Book[id]
   
   # Query books with a filter
   books = select(b for b in Book if b.read is True)
   ```

### Asset Pipeline

The project uses Flask-Assets for managing static assets:

1. **SASS**: CSS is generated from SASS files in `librium/static/sass/`.

2. **CoffeeScript**: JavaScript is generated from CoffeeScript files in `librium/static/coffee/`.

3. **Asset Bundles**: Asset bundles are defined in `librium/core/assets.py`.

### Code Style

1. **Python**: Follow PEP 8 guidelines for Python code.

2. **Templates**: Use consistent indentation in Jinja2 templates.

3. **CSS/SASS**: Use consistent naming conventions for CSS classes.

### Debugging

1. **Flask Debug Mode**: Run the application with `--debug` for detailed error messages.

2. **Database Logging**: Enable Pony ORM's SQL logging for debugging database operations:
   ```python
   from pony.orm import set_sql_debug

   set_sql_debug(True)
   ```