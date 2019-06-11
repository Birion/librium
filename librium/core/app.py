import os
import os.path
import pendulum
from dotenv import find_dotenv, load_dotenv
from flask import Flask, g
from pony.flask import Pony

# from handover.__version__ import __version__
# from handover.database.db import User
# from handover.views import main, action, task
# from .assets import assets

load_dotenv(find_dotenv())
