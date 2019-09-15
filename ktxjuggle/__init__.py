__version__ = '0.4.0'

# Public API
from ktxjuggle.ktx import Ktx

# Defer logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
