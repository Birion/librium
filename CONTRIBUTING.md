# Contributing to Librium

Thanks for your interest in contributing! This guide explains how to set up the project, follow our standards, and submit changes effectively.

Getting Started

1) Environment
- Python: 3.11 exactly
- Dependency manager: Pipenv
- OS: Cross-platform; dev notes assume Unix-like or Windows PowerShell

2) Setup
- Install Pipenv: `pip install pipenv`
- Install deps: `pipenv install`
- Activate shell: `pipenv shell`
- Environment variables: copy .env example if needed; common keys:
  - APPLICATION_NAME=Librium
  - DATABASE_URL=sqlite:///librium.sqlite
  - FLASK_ENV=development (testing for in-memory tests)
  - JWT_SECRET_KEY=dev-key-for-local (if touching JWT areas)

3) Running
- Dev server: `python -m flask --app librium:app run --debug`
- Tests: `python -m unittest tests/test_models.py -v` (or see docs/guidelines)

Branching and Commits
- Branch from main: `feature/<short-topic>` or `fix/<short-topic>`
- Keep commits focused and messages in imperative mood: "Add X", "Fix Y"
- Reference issues/tasks when relevant

Code Style
- Follow docs/code_style.md (PEP 8, typing, small functions, etc.)
- No print() in non-test code; use logging
- Keep view logic thin; push business logic to services

Database
- Use SQLAlchemy models in librium/database/sqlalchemy/db.py
- For schema changes, create Alembic migrations and update docs/database_schema.md

Testing
- Prefer isolated unit tests; for DB use in-memory SQLite in tests
- Avoid creating full Flask app unless necessary (see docs/guidelines)
- Ensure tests pass locally before opening PRs

Documentation
- Update docs alongside code (APIs, DB schema, behavior changes)
- Keep changelog entries in PR description when relevant

Pull Requests
- Include a clear summary of changes and rationale
- Note any migrations or breaking changes
- Add screenshots for UI changes
- Ensure linters/tests pass; include steps to reproduce fixes where applicable

Code Review
- Be respectful and constructive
- Review for clarity, correctness, and consistency
- Prefer suggestions with examples

Security
- Do not commit secrets; use environment variables
- Report security concerns privately to maintainers if available

License
- By contributing, you agree your contributions are licensed under the project’s LICENSE.

Thank you for helping improve Librium!