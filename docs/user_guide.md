# Librium User Guide

Welcome to Librium, a personal library manager. This guide helps you install, run, and use Librium to manage your books, authors, series, and more.

Contents
- Quick Start
- Installation and Setup
- Application Overview
- Managing Your Library
  - Books
  - Authors
  - Series
  - Publishers, Genres, Languages, Formats
- Finding and Organising
  - Search and Filters
  - Sorting and Pagination
  - Shelves/Collections (planned)
- Covers
- Import/Export
- Tips and Troubleshooting

Quick Start
1) Requirements
- Python 3.11
- Pipenv

2) Install
- Install Pipenv: `pip install pipenv`
- Install dependencies: `pipenv install`
- Activate environment: `pipenv shell`

3) Run the app
- Ensure .env contains basic config (see below)
- Start the server: `python -m flask --app librium:app run --debug`
- Open your browser at http://127.0.0.1:5000/

Configuration
Librium reads settings from environment variables (via .env):
- APPLICATION_NAME=Librium
- DATABASE_URL=sqlite:///librium.sqlite
- FLASK_ENV=development (use testing for ephemeral/in-memory tests)
- JWT_SECRET_KEY=dev-key-for-local (only needed for JWT-protected API parts)
Optional: LIBRIUM_CONFIG can point to a specific config class (see librium.core.config).

Application Overview
- Navigation: Use the top navigation to access Books, Authors, Series, and other sections.
- Layout: Lists support pagination and sorting; item pages allow editing and linking entities (authors, series, etc.).
- Status: Book lists can be toggled between unread/read/all using the on-page controls.

Managing Your Library

Books
- Create a book: Click “Add Book” and fill in mandatory fields (Title, Format). Optional fields include ISBN, Release Year, Page Count, Price, and Read status.
- Authors: Add one or more authors; you can reorder authors to affect display.
- Series: Add a series placement with an index to position a book within a series.
- Publishers, Genres, Languages: Select multiple values as needed.
- Covers: Upload a cover image (if enabled)—the UI indicates supported formats.
- Edit/Delete: Edit on the book detail page. Deleting performs a soft delete; items can be excluded from views by default.

Authors
- Create or search for authors by name. You can also set prefixes/suffixes if needed.
- Author pages show books, grouped by series or standalone.

Series
- Create series and add books to them with an index (1, 2, 3, ...). Lists indicate read/unread status across included books.

Publishers, Genres, Languages, Formats
- Manage these supporting entities from their respective pages or when editing books. Names are validated for length and cannot be empty.

Finding and Organising

Search and Filters
- Title search: Use the search box on the Books page to find titles containing your query (case-insensitive).
- Author search: Use the Authors page search to find names.
- ISBN lookup: The system will match ISBNs with or without hyphens/spaces.
- Read status: Toggle between unread/read/all—each click rotates the state.

Sorting and Pagination
- Sort by title, release year, author, or other available fields; the current sort option is shown in the list header.
- Pagination controls appear at the bottom of list pages; pick page size if available.

Covers
- If a book has a cover, the list and detail pages show it. You can upload or replace covers from the book form. Large images may be resized/compressed for performance.

Import/Export
- Export: Use the export function to download your library data as CSV/JSON (see the Export link or CLI utility if provided). A sample export.csv may be present for reference.
- Import: Planned features include importing by ISBN; for now, you can add books manually.

Tips and Troubleshooting
- Cannot start the app: Ensure you activated `pipenv shell` and are on Python 3.11.
- Database errors: Delete/backup librium.sqlite and restart, or ensure DATABASE_URL points to a writable location.
- Missing images: Ensure the covers/ directory is writable.
- API access: If using JWT-protected endpoints, set JWT_SECRET_KEY and consult API docs.

Getting Help
- Check README.md for a project overview.
- For developer setup and standards, see CONTRIBUTING.md and docs/code_style.md.
- Open an issue with details if you encounter a bug.
