# Load settings first
try:
    from settings import *
except ImportError:
    pass
  
# Now override any of them
DEBUG = False
SERVE_STATIC_FILES = False
