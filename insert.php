<?php
$servername = "localhost";
$username = "esp32_user";
$password = "sicheres_passwort";
$dbname = "esp32_db";

// Verbindung zur Datenbank herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung überprüfen
if ($conn->connect_error) {
    die("Verbindung fehlgeschlagen: " . $conn->connect_error);
}

// Überprüfen, ob die Daten vorhanden sind
if (isset($_POST['motion'])) {
    $motion = $_POST['motion'];

    // SQL-Query zum Einfügen der Daten in die Tabelle
    $sql = "INSERT INTO motion_log (motion_detected, timestamp) VALUES ('$motion', NOW())";

    if ($conn->query($sql) === TRUE) {
        echo "Daten erfolgreich eingefügt";
    } else {
        echo "Fehler: " . $conn->error;
    }
} else {
    echo "Keine Daten empfangen";
}

// Verbindung schließen
$conn->close();
?>
