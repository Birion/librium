import shutil
from pathlib import Path

from librium.database.pony.db import *

load_dotenv(find_dotenv())


def get_directory(directory):
    p = Path.cwd() / directory
    p.mkdir(exist_ok=True)
    return p


@db_session
def run():
    downloads_dir = Path(os.getenv("DOWNLOADS"))
    covers_dir = get_directory("covers")
    parent_dir = Path.cwd().parent

    for book in Book.select():
        file = downloads_dir / f"{book.isbn}.jpg"
        if file.exists():
            shutil.copy(file, covers_dir / f"{book.uuid}.jpg")
            shutil.copy(file, parent_dir / f"{book.uuid}.jpg")
            if not book.has_cover:
                book.has_cover = True

    commit()


if __name__ == "__main__":
    run()
