from datetime import datetime
from app import db

class Standort(db.Model):
    __tablename__ = 'standorte'

    id = db.Column(db.Integer, primary_key=True)
    strasse = db.Column(db.String(100), nullable=False)
    hausnummer = db.Column(db.String(10), nullable=False)
    plz = db.Column(db.String(10), nullable=False)
    stadt = db.Column(db.String(50), nullable=False)

    # Beziehung zu Briefkaesten
    briefkaesten = db.relationship('Briefkasten', backref='standort', lazy=True)

    def __repr__(self):
        return f'<Standort {self.strasse} {self.hausnummer}, {self.plz} {self.stadt}>'

class Briefkasten(db.Model):
    __tablename__ = 'briefkaesten'

    id = db.Column(db.Integer, primary_key=True)
    standort_id = db.Column(db.Integer, db.ForeignKey('standorte.id'), nullable=False)
    nummer = db.Column(db.String(50), nullable=False)

    # Beziehung zu ESP32Geraete
    geraete = db.relationship('ESP32Geraet', backref='briefkasten', lazy=True)

    def __repr__(self):
        return f'<Briefkasten {self.nummer} am Standort {self.standort_id}>'

class ESP32Geraet(db.Model):
    __tablename__ = 'esp32_geraete'

    id = db.Column(db.Integer, primary_key=True)
    briefkasten_id = db.Column(db.Integer, db.ForeignKey('briefkaesten.id'), nullable=False)
    mac_adresse = db.Column(db.String(17), unique=True, nullable=False)

    # Beziehung zu Bewegungsmeldungen
    bewegungen = db.relationship('Bewegungsmeldung', backref='geraet', lazy=True)

    def __repr__(self):
        return f'<ESP32Geraet {self.mac_adresse} am Briefkasten {self.briefkasten_id}>'

class Bewegungsmeldung(db.Model):
    __tablename__ = 'bewegungsmeldungen'

    id = db.Column(db.Integer, primary_key=True)
    esp32_id = db.Column(db.Integer, db.ForeignKey('esp32_geraete.id'), nullable=False)
    zeitstempel = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Bewegungsmeldung {self.id} von Gerät {self.esp32_id}>'
