from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="esp_user",            # Use your MySQL username
    password="esp_password",    # Use your MySQL password
    database="esp_data"         # The database for storing device data
)

# Endpoint for device registration
@app.route('/api/register', methods=['POST'])
def register_device():
    data = request.get_json()
    mac_address = data.get('mac_address')
    firmware_version = data.get('firmware_version')

    if not mac_address or not firmware_version:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    cursor = db.cursor()
    sql_devices = """
        INSERT INTO devices (mac_address, firmware_version)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE firmware_version = %s
    """
    try:
        cursor.execute(sql_devices, (mac_address, firmware_version, firmware_version))
        db.commit()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error registering device: {err}"}), 500

    sql_verwaltung = """
        INSERT INTO esp_verwaltung (esp_mac_address)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE esp_mac_address = esp_mac_address
    """
    try:
        cursor.execute(sql_verwaltung, (mac_address,))
        db.commit()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error adding device to esp_verwaltung: {err}"}), 500

    return jsonify({"success": True, "message": "Device registered and added to esp_verwaltung successfully"})

# Endpoint to log motion events
@app.route('/api/motion', methods=['POST'])
def log_motion_event():
    data = request.get_json()
    mac_address = data.get('mac_address')
    timestamp = data.get('timestamp')

    if not mac_address or not timestamp:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    now = datetime.now()
    event_date = now.date()  # YYYY-MM-DD
    event_time = now.time()  # HH:MM:SS

    cursor = db.cursor()
    sql = "INSERT INTO motion_events (mac_address, event_date, event_time) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (mac_address, event_date, event_time))
        db.commit()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error logging motion event: {err}"}), 500

    return jsonify({"success": True, "message": "Motion event logged successfully"})

# Endpoint to update system information
@app.route('/api/system-info', methods=['POST'])
def update_system_info():
    data = request.get_json()
    mac_address = data.get('mac_address')
    public_ip = data.get('public_ip')
    wifi_strength = data.get('wifi_strength')
    serial_number = data.get('serial_number')
    uptime = data.get('uptime')
    firmware_version = data.get('firmware_version')

    if not mac_address:
        return jsonify({"success": False, "message": "MAC address is required"}), 400

    cursor = db.cursor()
    sql = """
        INSERT INTO esp_info (mac_address, public_ip, wifi_strength, serial_number, uptime, firmware_version, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            public_ip = VALUES(public_ip),
            wifi_strength = VALUES(wifi_strength),
            serial_number = VALUES(serial_number),
            uptime = VALUES(uptime),
            firmware_version = VALUES(firmware_version),
            last_seen = NOW()
    """
    try:
        cursor.execute(sql, (mac_address, public_ip, wifi_strength, serial_number, uptime, firmware_version))
        db.commit()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error updating system info: {err}"}), 500

    return jsonify({"success": True, "message": "System info updated successfully"})

# Endpoint to fetch registered ESP devices
@app.route('/api/esp-liste', methods=['GET'])
def fetch_esp_liste():
    cursor = db.cursor(dictionary=True)
    sql = """
        SELECT d.mac_address, i.last_seen,
               IF(TIMESTAMPDIFF(MINUTE, i.last_seen, NOW()) < 2, 'online', 'offline') AS status
        FROM devices d
        LEFT JOIN esp_info i ON d.mac_address = i.mac_address
    """
    try:
        cursor.execute(sql)
        devices = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error fetching ESP list: {err}"}), 500

    return jsonify({"success": True, "devices": devices})

# Endpoint to fetch detailed information for a specific ESP device
@app.route('/api/esp-details', methods=['GET'])
def fetch_esp_details():
    mac_address = request.args.get('mac_address')

    if not mac_address:
        return jsonify({"success": False, "message": "MAC address is required"}), 400

    cursor = db.cursor(dictionary=True)
    sql = """
        SELECT d.mac_address, d.firmware_version, e.standort_id, s.vorname, s.nachname, s.strasse, s.hausnummer, s.plz, s.stadt,
               i.public_ip, i.serial_number, i.uptime, i.wifi_strength, i.last_seen
        FROM devices d
        LEFT JOIN esp_verwaltung e ON d.mac_address = e.esp_mac_address
        LEFT JOIN standorte s ON e.standort_id = s.id
        LEFT JOIN esp_info i ON d.mac_address = i.mac_address
        WHERE d.mac_address = %s
    """
    try:
        cursor.execute(sql, (mac_address,))
        results = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error fetching ESP details: {err}"}), 500

    if len(results) == 0:
        return jsonify({"success": False, "message": "Device not found"}), 404

    device = results[0]
    standort = f"{device['vorname'] or 'unbekannt'} {device['nachname'] or ''}, {device['strasse'] or 'unbekannt'} {device['hausnummer'] or ''}, {device['plz'] or 'unbekannt'} {device['stadt'] or 'unbekannt'}"

    return jsonify({
        "success": True,
        "details": {
            "mac_address": device['mac_address'],
            "firmware_version": device['firmware_version'] or 'unbekannt',
            "standort": standort,
            "public_ip": device['public_ip'] or 'unbekannt',
            "serial_number": device['serial_number'] or 'unbekannt',
            "wifi_strength": device['wifi_strength'] if device['wifi_strength'] is not None else 'unbekannt',
            "uptime": device['uptime'] if device['uptime'] is not None else 'unbekannt',
            "last_seen": device['last_seen'] or 'unbekannt'
        }
    })

# Endpoint to fetch motion events for a specific ESP32 device
@app.route('/api/motions', methods=['GET'])
def fetch_motion_events():
    mac_address = request.args.get('mac_address')

    if not mac_address:
        return jsonify({"success": False, "message": "MAC address is required"}), 400

    cursor = db.cursor(dictionary=True)
    sql = """
        SELECT mac_address, event_date, event_time
        FROM motion_events
        WHERE mac_address = %s
        ORDER BY event_date DESC, event_time DESC
    """
    try:
        cursor.execute(sql, (mac_address,))
        results = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error fetching motion events: {err}"}), 500

    if len(results) == 0:
        return jsonify({"success": False, "message": "No motion events found"}), 404

    return jsonify({"success": True, "motion_events": results})

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
