# from .gui import app

# TODO(Bradley): Need to detect Qt or Gtk and switch appropriately. Also,
# should try to abstract away UI library differences if possible.
from .qt.main import *


def mats_ui_dir():
    return __file__
