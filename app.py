from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from datetime import datetime

# Flask-Anwendung initialisieren
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelle importieren
from models import Standort, Briefkasten, ESP32Geraet, Bewegungsmeldung

# API-Schlüssel aus der Konfiguration laden
API_KEY = app.config['API_KEY']

# Funktion zur Überprüfung des API-Schlüssels
def check_api_key():
    key = request.headers.get('X-API-Key')
    if not key or key != API_KEY:
        abort(401, description="Unauthorized")

# Registrierungs-Endpunkt
@app.route('/api/register', methods=['POST'])
def register_device():
    check_api_key()
    data = request.get_json()
    if not data or 'mac_adresse' not in data or 'briefkasten_nummer' not in data:
        return jsonify({'success': False, 'message': 'Ungültige Daten'}), 400

    mac_adresse = data['mac_adresse']
    briefkasten_nummer = data['briefkasten_nummer']

    # Briefkasten suchen
    briefkasten = Briefkasten.query.filter_by(nummer=briefkasten_nummer).first()
    if not briefkasten:
        return jsonify({'success': False, 'message': 'Briefkasten nicht gefunden'}), 400

    # Gerät registrieren
    geraet = ESP32Geraet.query.filter_by(mac_adresse=mac_adresse).first()
    if geraet:
        return jsonify({'success': True, 'message': 'Gerät bereits registriert'}), 200
    else:
        neues_geraet = ESP32Geraet(
            mac_adresse=mac_adresse,
            briefkasten_id=briefkasten.id
        )
        db.session.add(neues_geraet)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Gerät erfolgreich registriert'}), 201

# Bewegungsmeldungs-Endpunkt
@app.route('/api/motion', methods=['POST'])
def motion_event():
    check_api_key()
    data = request.get_json()
    if not data or 'mac_adresse' not in data or 'status' not in data:
        return jsonify({'success': False, 'message': 'Ungültige Daten'}), 400

    mac_adresse = data['mac_adresse']
    status = data['status']

    # Gerät suchen
    geraet = ESP32Geraet.query.filter_by(mac_adresse=mac_adresse).first()
    if not geraet:
        return jsonify({'success': False, 'message': 'Gerät nicht registriert'}), 400

    neue_bewegung = Bewegungsmeldung(
        esp32_id=geraet.id,
        zeitstempel=datetime.utcnow(),
        status=bool(status)
    )
    db.session.add(neue_bewegung)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bewegungsmeldung gespeichert'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
