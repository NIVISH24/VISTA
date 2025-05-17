-- Mouse events table
CREATE TABLE IF NOT EXISTS mouse_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    x INTEGER,
    y INTEGER,
    interval FLOAT,
    device_fingerprint VARCHAR(64),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Keystroke events table
CREATE TABLE IF NOT EXISTS keystroke_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    key_pressed VARCHAR(50) NOT NULL,
    interval FLOAT,
    device_fingerprint VARCHAR(64),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System info table
CREATE TABLE IF NOT EXISTS system_info (
    id SERIAL PRIMARY KEY,
    recorded_time TIMESTAMP NOT NULL,
    mac_address VARCHAR(17),
    cpu_info TEXT,
    disk_info TEXT,
    memory_info BIGINT,
    hostname VARCHAR(255),
    os_info TEXT,
    device_fingerprint VARCHAR(64),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USB events table
CREATE TABLE IF NOT EXISTS usb_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    action VARCHAR(10) NOT NULL,
    vendor_id VARCHAR(8),
    product_id VARCHAR(8),
    vendor_name TEXT,
    product_name TEXT,
    serial_number TEXT,
    device_fingerprint VARCHAR(64),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voice recording events table
CREATE TABLE IF NOT EXISTS voice_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    file_path TEXT,
    duration FLOAT,
    sample_rate INTEGER,
    device_fingerprint VARCHAR(64),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);