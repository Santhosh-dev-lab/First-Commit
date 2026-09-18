import uuid

from pydantic import BaseModel

from app.db.database import get_db


class FarmConfig(BaseModel):
    name: str
    organization: str | None = None
    country: str | None = None
    region: str | None = None
    timezone: str | None = None

class EnvironmentConfig(BaseModel):
    type: str
    area_sqm: float
    length_m: float | None = None
    width_m: float | None = None
    height_m: float | None = None

class ZoneConfig(BaseModel):
    name: str
    area_sqm: float
    crop_id: str | None = None
    growth_stage: str | None = None

class ResourceConfig(BaseModel):
    tank_capacity_l: float | None = None
    current_water_l: float | None = None
    energy_source: str | None = None

class DeviceConfig(BaseModel):
    zone_id: str | None = None
    name: str
    type: str
    capability: str | None = None
    mode: str | None = "SIMULATED"

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
        conn.commit()
        conn.close()

    @staticmethod
    def save_farm(user_id: str, config: FarmConfig) -> str:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if farm exists
        cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            farm_id = row['id']
            cursor.execute(
                "UPDATE farms SET name=?, organization=?, country=?, region=?, timezone=? WHERE id=?",
                (config.name, config.organization, config.country, config.region, config.timezone, farm_id)
            )
        else:
            farm_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO farms (id, user_id, name, organization, country, region, timezone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (farm_id, user_id, config.name, config.organization, config.country, config.region, config.timezone)
            )
            
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
        
        cursor.execute("SELECT id FROM environments WHERE farm_id = ?", (farm_id,))
        row = cursor.fetchone()
        
        if row:
            env_id = row['id']
            cursor.execute(
                "UPDATE environments SET type=?, area_sqm=?, length_m=?, width_m=?, height_m=? WHERE id=?",
                (config.type, config.area_sqm, config.length_m, config.width_m, config.height_m, env_id)
            )
        else:
            env_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO environments (id, farm_id, type, area_sqm, length_m, width_m, height_m) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (env_id, farm_id, config.type, config.area_sqm, config.length_m, config.width_m, config.height_m)
            )
            
        conn.commit()
        conn.close()
        return env_id

    @staticmethod
    def save_zones(user_id: str, configs: list[ZoneConfig]) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT environments.id FROM environments JOIN farms ON environments.farm_id = farms.id WHERE farms.user_id = ?", (user_id,))
        env = cursor.fetchone()
        if not env:
            raise ValueError("Environment not found")
        env_id = env['id']
        
        cursor.execute("DELETE FROM zones WHERE environment_id = ?", (env_id,))
        
        for config in configs:
            zone_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO zones (id, environment_id, name, area_sqm, crop_id, growth_stage) VALUES (?, ?, ?, ?, ?, ?)",
                (zone_id, env_id, config.name, config.area_sqm, config.crop_id, config.growth_stage)
            )
            
        conn.commit()
        conn.close()

    @staticmethod
    def save_resources(user_id: str, config: ResourceConfig) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT environments.id FROM environments JOIN farms ON environments.farm_id = farms.id WHERE farms.user_id = ?", (user_id,))
        env = cursor.fetchone()
        if not env:
            raise ValueError("Environment not found")
        env_id = env['id']
        
        cursor.execute("SELECT id FROM resources WHERE environment_id = ?", (env_id,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute(
                "UPDATE resources SET tank_capacity_l=?, current_water_l=?, energy_source=? WHERE environment_id=?",
                (config.tank_capacity_l, config.current_water_l, config.energy_source, env_id)
            )
        else:
            res_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO resources (id, environment_id, tank_capacity_l, current_water_l, energy_source) VALUES (?, ?, ?, ?, ?)",
                (res_id, env_id, config.tank_capacity_l, config.current_water_l, config.energy_source)
            )
            
        conn.commit()
        conn.close()

    @staticmethod
    def save_devices(user_id: str, configs: list[DeviceConfig]) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT environments.id FROM environments JOIN farms ON environments.farm_id = farms.id WHERE farms.user_id = ?", (user_id,))
        env = cursor.fetchone()
        if not env:
            raise ValueError("Environment not found")
        env_id = env['id']
        
        cursor.execute("DELETE FROM devices WHERE environment_id = ?", (env_id,))
        
        for config in configs:
            dev_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO devices (id, environment_id, zone_id, name, type, capability, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (dev_id, env_id, config.zone_id, config.name, config.type, config.capability, config.mode)
            )
            
        conn.commit()
        conn.close()
