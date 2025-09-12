# Librium Code Style Guide

This document codifies the conventions used in the Librium project to keep the codebase readable and consistent.

General Principles
- Prefer clarity over cleverness.
- Keep functions small and focused; extract helpers when logic grows.
- Write docstrings and type hints for public functions in core modules.
- Maintain consistent naming and structure across modules.

Python
- Version: Target Python 3.11 exactly.
- Style: PEP 8 with sensible line length (black-ish 100–120 cols acceptable if it improves readability).
- Imports: standard library, third-party, local, separated by blank lines; avoid unused imports.
- Typing: Use typing and typing_extensions as in core; annotate public functions, return types, and dataclass/ORM fields where practical.
- Docstrings: Use Google-style or reST consistently within a file; include Args/Returns/Raises for nontrivial functions.
- Logging: Use the configured logging utilities; no print() in production code.
- Errors: Raise specific exceptions; let the view layer transform them into HTTP responses.
- SQLAlchemy: Use models from librium.database.sqlalchemy.db; prefer session-local patterns in services; avoid committing in deep helper functions.
- Validation: Keep input validation close to model/service boundaries; reuse existing validator helpers.

Flask Views and Services
- Keep view functions thin; delegate to services for business logic.
- Return consistent JSON error shapes from APIs, as implemented in the project.
- Use blueprints registered in create_app; avoid side effects at import time.

Templates (Jinja)
- Indentation: 2 spaces for HTML/Jinja blocks.
- Filters/Helpers: Prefer using registered filters/utilities (e.g., parse_read_arg) rather than re-implementing in templates.
- Blocks: Keep templates small; use includes for shared components (_core header/footer).
- i18n: Write human-friendly text; avoid hard-coded magic values.

CSS/SASS
- Structure: Use partials and components under librium/static/sass; one component per file when practical.
- Naming: BEM-inspired (block__element--modifier) where helpful.
- Variables/Mixins: Centralize in partials; avoid duplicating colors and spacing.
- Responsiveness: Prefer mobile-first media queries; test at common breakpoints (≤480, 768, 1024, ≥1280).

JavaScript/CoffeeScript
- Prefer small, unobtrusive behaviours; progressive enhancement where possible.
- Avoid global symbols; wrap modules or use IIFEs.
- Use data-attributes for hooks; keep DOM querying scoped.

Testing
- Unit tests: unittest; keep tests deterministic and isolated. For DB models, prefer in-memory SQLite engines.
- API tests: Mock service layers; avoid booting the full app unless necessary.
- Names: test_*.py with clear TestCase names.

Commit/PR Hygiene
- One logical change per commit; meaningful messages in imperative mood.
- Keep PRs small; include a summary of changes and any migration notes.

Documentation
- Update docs alongside code changes, especially when changing the database schema or public APIs.

Adoption
- This guide is lightweight; if a decision isn’t covered here, follow the surrounding code’s conventions.
