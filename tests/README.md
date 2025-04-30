# Librium Test Suite

This directory contains comprehensive tests for the Librium application. The tests are organized by component and use Python's unittest framework.

## Test Structure

The test suite is organized into the following files:

- `test_models.py`: Tests for database models and their relationships
- `test_api.py`: Tests for API endpoints
- `test_views.py`: Tests for view functions and routes
- `test_utilities.py`: Tests for utility functions and schemas

## Running Tests

### Running All Tests

To run all tests, use the following command from the project root:

```bash
python -m unittest discover -s tests
```

### Running Individual Test Files

To run tests from a specific file:

```bash
python -m unittest tests/test_models.py
```

### Running Specific Test Cases or Methods

To run a specific test case:

```bash
python -m unittest tests.test_models.TestBook
```

To run a specific test method:

```bash
python -m unittest tests.test_models.TestBook.test_create_book
```

## Test Configuration

All tests use an in-memory SQLite database to avoid affecting the production database. This is configured by setting the `PONY_SQLDATABASE` environment variable to `:memory:` before importing the database models.

## Test Coverage

### Database Models (`test_models.py`)

Tests for:
- Creating, updating, and deleting books
- Book properties and relationships
- Author creation and book relationships
- Series properties and book relationships
- SeriesIndex properties

### API Endpoints (`test_api.py`)

Tests for:
- GET endpoints (series, genres, languages, publishers)
- POST endpoints for adding entities (genre, publisher, language, series, author)
- DELETE endpoint for books
- Cover image upload
- Export functionality

### Views and Routes (`test_views.py`)

Tests for:
- Book detail view (GET and POST)
- Book add view (GET and POST)
- Main index view

### Utilities (`test_utilities.py`)

Tests for:
- Custom boolean field
- Series schema validation
- Book schema validation and transformation
- ISBN formatting
- JSON parsing for series data

## Adding New Tests

When adding new tests:

1. Follow the existing pattern of test organization
2. Use the `@db_session` decorator for tests that interact with the database
3. Clean up any test data in the `setUp` or `tearDown` methods
4. Use descriptive test method names that indicate what is being tested
5. Include assertions that verify both the response and the database state

## Mocking

For tests that involve external dependencies (like file operations), use the `unittest.mock` module to mock these dependencies. See examples in `test_api.py` for how to mock file operations.