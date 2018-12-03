# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
APP_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.join(APP_ROOT, 'app')
APP_STATIC = os.path.join(APP_ROOT, 'static')

API_URL = '/api/v1'

# Define the images directory

IMAGE_URL_BASE = "/static/images"
IMAGE_DIR = os.path.join(APP_STATIC, 'images')

# Define the puplic IP address
PUBLIC_URL = "http://localhost:8080"

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'postgresql://catalog:123@localhost/catalog'
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"


SQLALCHEMY_TRACK_MODIFICATIONS = False
