# Librium FAQ

This Frequently Asked Questions section answers common questions about installing, running, and using Librium.

## General

Q: What are the system requirements?\
A: Python 3.11 and Pipenv. Librium uses SQLite by default and runs locally.

Q: How do I start the application?\
A: From an activated Pipenv shell, run: `python -m flask --app librium:app run --debug` and open http://127.0.0.1:5000/.

Q: Where is my data stored?\
A: By default in librium.sqlite in the project root. You can change it via DATABASE_URL in .env.

## Library Management

Q: How do I add a new book?\
A: Go to Books and click “Add Book.” Enter a title and select a format; optionally provide ISBN, release year, authors, etc.

Q: Can I mark books as read/unread?\
A: Yes. Use the “Read” checkbox on the book form. In lists, you can toggle between unread/read/all.

Q: How do I organise books into series?\
A: Create a series and assign an index to each book (1, 2, 3, ...). The series page shows order and read status.

Q: Can a book have multiple authors or genres?\
A: Yes. Use the multi-select controls to add multiple authors, genres, languages, and publishers.

## Covers

Q: How do I add or change a cover image?\
A: On the book page, click the cover upload area (or Replace cover) and select an image file.

Q: Where are cover images stored?\
A: In the covers/ directory (or configured storage). The filename is the book’s UUID with .jpg.

## Import/Export

Q: How do I export my library?\
A: Use the Export action in the UI (or the API endpoint). Exports are available as CSV/JSON.

Q: Can I import books by ISBN?\
A: Import by ISBN is planned. For now, add books manually.

## Troubleshooting

Q: I get a database error or cannot write to the DB.\
A: Ensure DATABASE_URL points to a writable path. If the file is corrupted, back it up and let the app recreate it.

Q: Login prompts keep failing.\
A: Ensure JWT config is set if using protected API routes. In development, some features may be available without login.

Q: Images don’t appear after upload.\
A: Confirm the covers/ directory is writable and that the image meets size/format expectations.

---

Need More Help?
- Read docs/user_guide.md for a full walkthrough.
- Check README.md for overview.
- Open an issue with steps to reproduce any problems you encounter.
