# Vercel entrypoint for Flask (WSGI)
# This imports the Flask app from Recommendation_system/app.py

import os
import sys

# Ensure the app folder is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
APP_DIR = os.path.join(PROJECT_ROOT, "Recommendation_system")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Import the Flask app object
from app import app  # noqa: E402

# On Vercel Python, exporting a module-level `app` WSGI object is supported.
# All routes will be routed here via vercel.json rewrites.
