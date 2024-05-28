import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from flask import Blueprint

load_dotenv(find_dotenv())

covers_folder = os.getenv("COVERS_FOLDER") if os.getenv("COVERS_FOLDER") else "covers"

bp = Blueprint(
    "covers",
    __name__,
    static_folder=Path(covers_folder).resolve(),
    static_url_path="/covers",
)
