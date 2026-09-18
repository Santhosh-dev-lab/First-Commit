import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "physica.db"

def get_db():
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
        created_at REAL NOT NULL
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
        organization TEXT,
        country TEXT,
        region TEXT,
        timezone TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS environments (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        type TEXT NOT NULL,
        area_sqm REAL NOT NULL,
        length_m REAL,
        width_m REAL,
        height_m REAL,
        FOREIGN KEY (farm_id) REFERENCES farms(id)
    );

    CREATE TABLE IF NOT EXISTS zones (
        id TEXT PRIMARY KEY,
        environment_id TEXT NOT NULL,
        name TEXT NOT NULL,
        area_sqm REAL NOT NULL,
        crop_id TEXT,
        growth_stage TEXT,
        FOREIGN KEY (environment_id) REFERENCES environments(id)
    );

    CREATE TABLE IF NOT EXISTS resources (
        id TEXT PRIMARY KEY,
        environment_id TEXT NOT NULL,
        tank_capacity_l REAL,
        current_water_l REAL,
        energy_source TEXT,
        FOREIGN KEY (environment_id) REFERENCES environments(id)
    );

    CREATE TABLE IF NOT EXISTS devices (
        id TEXT PRIMARY KEY,
        environment_id TEXT NOT NULL,
        zone_id TEXT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        capability TEXT,
        mode TEXT,
        FOREIGN KEY (environment_id) REFERENCES environments(id),
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );

    CREATE TABLE IF NOT EXISTS onboarding_status (
        user_id TEXT PRIMARY KEY,
        is_complete BOOLEAN NOT NULL DEFAULT 0,
        current_step INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
