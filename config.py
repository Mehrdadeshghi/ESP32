import os

class Config:
    # Secret Key für Flask-Anwendung
    SECRET_KEY = os.environ.get('SECRET_KEY', 'DEIN_SECRET_KEY')

    # Datenbankkonfiguration
    DB_USER = os.environ.get('DB_USER', 'DEIN_DB_BENUTZER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'DEIN_DB_PASSWORT')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')  # Oder die IP-Adresse deines Datenbankservers
    DB_NAME = os.environ.get('DB_NAME', 'esp32_db')

    SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API-Schlüssel für die Authentifizierung
    API_KEY = os.environ.get('API_KEY', 'DEIN_API_KEY')
