import shutil
from pathlib import Path
from uuid import UUID

from librium.database.pony.db import *


@db_session
def run():
    p = Path("/home/ondra/Stažené")
    pc = Path(".") / ".."
    print(pc.resolve())

    for book in Book.select():
        file = p / f"{book.isbn}.jpg"
        if file.exists():
            new_file = pc / "covers" / f"{book.uuid}.jpg"
            new_file2 = pc / f"{book.uuid}.jpg"
            new_file_temp = pc / "covers_new" / f"{UUID(book.uuid).hex}.jpg"
            shutil.copy(file, new_file)
            shutil.copy(file, new_file2)
            shutil.copy(file, new_file_temp)
            if not book.has_cover:
                book.has_cover = True
    commit()


if __name__ == "__main__":
    run()
