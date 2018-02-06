# flake8: noqa
from writlarge.settings_shared import *

try:
    from writlarge.local_settings import *
except ImportError:
    pass
