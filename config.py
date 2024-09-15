import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey123')
    DB_USER = os.environ.get('DB_USER', 'esp32_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password123')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'esp32_db')

    SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_KEY = os.environ.get('API_KEY', '1234567890abcdef1234567890abcdef')
