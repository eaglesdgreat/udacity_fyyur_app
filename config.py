import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'eagles')
POSTGRES_PASS = os.environ.get('POSTGRES_PASS', '')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'eagles')

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@/%s' % (
  POSTGRES_USER,
  POSTGRES_PASS,
  # POSTGRES_HOST,
  # POSTGRES_PORT,
  POSTGRES_DB
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
