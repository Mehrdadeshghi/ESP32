CREATE TABLE motion_log (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    motion_detected BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
