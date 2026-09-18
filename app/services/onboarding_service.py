import json
import time
import uuid

from pydantic import BaseModel

from app.db.database import get_db


class FarmConfig(BaseModel):
    name: str
    location: str | None = None

class EnvironmentConfig(BaseModel):
    type: str
    area_sqm: float

class ZoneConfig(BaseModel):
    name: str
    area_sqm: float
    crop_id: str | None = None
    growth_stage: str | None = None

class ResourceConfig(BaseModel):
    tank_capacity_l: float | None = None
    energy_source: str | None = None

class DeviceConfig(BaseModel):
    zone_id: str | None = None
    name: str
    type: str

class FarmConnectionConfig(BaseModel):
    mode: str

class OnboardingStatus(BaseModel):
    completed: bool
    current_step: int

class OnboardingService:
    @staticmethod
    def get_status(user_id: str) -> OnboardingStatus:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_complete, current_step FROM onboarding_status WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return OnboardingStatus(completed=False, current_step=1)
        return OnboardingStatus(completed=bool(row['is_complete']), current_step=row['current_step'])
        
    @staticmethod
    def update_step(user_id: str, step: int) -> None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE onboarding_status SET current_step = ? WHERE user_id = ?", (step, user_id))
        conn.commit()
        conn.close()
        
    @staticmethod
    def complete_onboarding(user_id: str) -> None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE onboarding_status SET is_complete = 1 WHERE user_id = ?", (user_id,))
        # Also mark the farm as onboarding_completed
        cursor.execute("UPDATE farms SET onboarding_completed = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def save_farm(user_id: str, config: FarmConfig) -> str:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        now = time.time()
        if row:
            farm_id = row['id']
            cursor.execute(
                "UPDATE farms SET name=?, location=?, updated_at=? WHERE id=?",
                (config.name, config.location, now, farm_id)
            )
        else:
            farm_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO farms (id, user_id, name, location, created_at, updated_at, onboarding_completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (farm_id, user_id, config.name, config.location, now, now, 0)
            )
            # Create onboarding status if missing
            cursor.execute("INSERT OR IGNORE INTO onboarding_status (user_id, is_complete, current_step) VALUES (?, 0, 1)", (user_id,))
            
        conn.commit()
        conn.close()
        return farm_id

    @staticmethod
    def save_environment(user_id: str, config: EnvironmentConfig) -> str:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        if not farm:
            raise ValueError("Farm not found")
        farm_id = farm['id']
        
        cursor.execute(
            "UPDATE farms SET environment_type=?, area_m2=?, updated_at=? WHERE id=?",
            (config.type, config.area_sqm, time.time(), farm_id)
        )
            
        conn.commit()
        conn.close()
        return farm_id

    @staticmethod
    def save_zones(user_id: str, configs: list[ZoneConfig]) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        if not farm:
            raise ValueError("Farm not found")
        farm_id = farm['id']
        
        cursor.execute("DELETE FROM zones WHERE farm_id = ?", (farm_id,))
        
        for config in configs:
            zone_id = str(uuid.uuid4())
            # Basic validation
            if config.crop_id and config.crop_id.strip() == "":
                config.crop_id = None
                
            cursor.execute(
                "INSERT INTO zones (id, farm_id, name, area_m2, crop_id, growth_stage, configuration) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (zone_id, farm_id, config.name, config.area_sqm, config.crop_id, config.growth_stage, json.dumps({}))
            )
            
        conn.commit()
        conn.close()

    @staticmethod
    def save_resources(user_id: str, config: ResourceConfig) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        if not farm:
            raise ValueError("Farm not found")
        farm_id = farm['id']
        
        cursor.execute("SELECT id FROM resources WHERE farm_id = ?", (farm_id,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute(
                "UPDATE resources SET tank_capacity_l=?, energy_source=? WHERE farm_id=?",
                (config.tank_capacity_l, config.energy_source, farm_id)
            )
        else:
            res_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO resources (id, farm_id, tank_capacity_l, energy_source) VALUES (?, ?, ?, ?)",
                (res_id, farm_id, config.tank_capacity_l, config.energy_source)
            )
            
        conn.commit()
        conn.close()

    @staticmethod
    def save_devices(user_id: str, configs: list[DeviceConfig]) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        if not farm:
            raise ValueError("Farm not found")
        farm_id = farm['id']
        
        cursor.execute("DELETE FROM devices WHERE farm_id = ?", (farm_id,))
        
        for config in configs:
            dev_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO devices (id, farm_id, zone_id, name, device_type, protocol, status, last_seen, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (dev_id, farm_id, config.zone_id, config.name, config.type, "virtual", "OFFLINE", time.time(), json.dumps({}))
            )
            
        conn.commit()
        conn.close()

    @staticmethod
    def save_connection(user_id: str, config: FarmConnectionConfig) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        if not farm:
            raise ValueError("Farm not found")
        farm_id = farm['id']
        
        # Mode is LOCAL_SIMULATION, EDGE_GATEWAY, or CONNECT_LATER
        status = "CONNECTED" if config.mode == "LOCAL_SIMULATION" else "NOT_CONFIGURED"
        now = time.time()
        
        cursor.execute("SELECT id FROM farm_connections WHERE farm_id = ?", (farm_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE farm_connections SET mode=?, status=?, updated_at=? WHERE farm_id=?",
                (config.mode, status, now, farm_id)
            )
        else:
            conn_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO farm_connections (id, farm_id, mode, status, gateway_id, last_seen, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (conn_id, farm_id, config.mode, status, None, now, now, now)
            )
            
        conn.commit()
        conn.close()
