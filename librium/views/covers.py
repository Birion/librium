from flask import Blueprint

from pathlib import Path

bp = Blueprint("covers", __name__, static_folder=Path("covers").resolve(), static_url_path="/covers")
