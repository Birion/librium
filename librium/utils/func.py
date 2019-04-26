import inspect
from pathlib import Path

from kivy.lang import Builder


def load_kv():
    """
    This magical function lookup module name, and load the kv file
    with the same name (in the same directory)
    """
    filename = Path(inspect.currentframe().f_back.f_code.co_filename)
    f = filename.with_suffix(".kv")
    if f.exists() and str(f) not in Builder.files:
        Builder.load_file(str(f))
