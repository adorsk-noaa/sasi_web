import sys, os, logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, os.path.dirname(__file__))
from results_app import app as application
