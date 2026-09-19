import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "physica.db"

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # create db directory if not exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at REAL NOT NULL,
        role TEXT DEFAULT 'OWNER'
    );

    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at REAL NOT NULL,
        expires_at REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS farms (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        location TEXT,
        area_m2 REAL,
        environment_type TEXT,
        created_at REAL,
        updated_at REAL,
        onboarding_completed BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS zones (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        name TEXT NOT NULL,
        area_m2 REAL NOT NULL,
        crop_id TEXT,
        growth_stage TEXT,
        configuration TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );

    CREATE TABLE IF NOT EXISTS resources (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        tank_capacity_l REAL,
        energy_source TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );

    CREATE TABLE IF NOT EXISTS farm_connections (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        status TEXT NOT NULL,
        gateway_id TEXT,
        last_seen REAL,
        created_at REAL,
        updated_at REAL,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );

    CREATE TABLE IF NOT EXISTS devices (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        zone_id TEXT,
        name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        protocol TEXT,
        status TEXT,
        last_seen REAL,
        metadata TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id),
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );

    CREATE TABLE IF NOT EXISTS sensors (
        id TEXT PRIMARY KEY,
        device_id TEXT NOT NULL,
        farm_id TEXT NOT NULL,
        zone_id TEXT,
        sensor_type TEXT NOT NULL,
        unit TEXT,
        status TEXT,
        last_reading_at REAL,
        FOREIGN KEY (device_id) REFERENCES devices(id),
        FOREIGN KEY (farm_id) REFERENCES farms(id),
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );

    CREATE TABLE IF NOT EXISTS actuators (
        id TEXT PRIMARY KEY,
        device_id TEXT NOT NULL,
        farm_id TEXT NOT NULL,
        zone_id TEXT,
        actuator_type TEXT NOT NULL,
        status TEXT,
        last_command_at REAL,
        FOREIGN KEY (device_id) REFERENCES devices(id),
        FOREIGN KEY (farm_id) REFERENCES farms(id),
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );

    CREATE TABLE IF NOT EXISTS telemetry_records (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        zone_id TEXT,
        timestamp REAL NOT NULL,
        measurements TEXT NOT NULL,
        source TEXT NOT NULL,
        FOREIGN KEY (farm_id) REFERENCES farms(id),
        FOREIGN KEY (device_id) REFERENCES devices(id),
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );

    CREATE TABLE IF NOT EXISTS onboarding_status (
        user_id TEXT PRIMARY KEY,
        is_complete BOOLEAN NOT NULL DEFAULT 0,
        current_step INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        timestamp REAL NOT NULL,
        event_type TEXT NOT NULL,
        user_id TEXT,
        farm_id TEXT,
        resource_id TEXT,
        request_id TEXT,
        result TEXT NOT NULL,
        metadata TEXT
    );

    CREATE TABLE IF NOT EXISTS password_resets (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at REAL NOT NULL,
        expires_at REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS command_execution_log (
        id TEXT PRIMARY KEY,
        command_id TEXT UNIQUE NOT NULL,
        farm_id TEXT NOT NULL,
        executed_at REAL NOT NULL,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );

    CREATE TABLE IF NOT EXISTS virtual_farm_runs (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        config TEXT NOT NULL,
        status TEXT NOT NULL,
        current_time REAL NOT NULL,
        scenario TEXT NOT NULL,
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
