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
   SQLDATABASE=librium.sqlite       # Path to the SQLite database file
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

   os.environ["SQLDATABASE"] = ":memory:"
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

3. **Database Tests**: When testing database operations, use the `@transactional` decorator and create an in-memory database.

## Additional Development Information

### Project Structure

- **librium/core/**: Core application components
- **librium/database/**: Database models and configuration
- **librium/static/**: Static assets (CSS, JavaScript, images)
- **librium/templates/**: Jinja2 templates
- **librium/views/**: Flask blueprints and view functions

### Database ORM

Librium uses SQLAlchemy for database operations. Key points:

1. **Entity Definitions**: Database models are defined in `librium/database/sqlalchemy/db.py`.

2. **Database Sessions**: Use the `@transactional` or `@read_only` decorators for functions that interact with the database.

3. **Queries**: Use SQLAlchemy's query language for database operations.

4. **Compatibility Layer**: The project maintains compatibility with Pony ORM naming conventions through a compatibility layer.

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

2. **Database Logging**: Enable SQLAlchemy's SQL logging for debugging database operations
