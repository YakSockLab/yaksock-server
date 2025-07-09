import os

DB_CONFIG = {
    'dbname': os.environ.get('DB_NAME', 'yaksockdb'),
    'user': os.environ.get('DB_USER', 'yaksock'),
    'password': os.environ.get('DB_PASSWORD', 'yaksock1234!'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}