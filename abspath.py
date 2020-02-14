# nifty trick to enable use of root-relative paths; especially useful when modularizing webapp responders
# -- to be successful, this has to be in the top-level directory of the application

import os

root = os.path.dirname(__file__)
