import time

from .models import ClockMode


class SimulationClock:
    def __init__(self, mode: ClockMode, start_time: float | None = None, speedup_factor: float = 60.0):
        self.mode = mode
        self.start_wall_time = time.time()
        self.start_sim_time = start_time if start_time is not None else self.start_wall_time
        self.current_sim_time = self.start_sim_time
        self.last_tick_wall_time = self.start_wall_time
        self.speedup_factor = speedup_factor
        
    def advance(self, step_size_hours: float) -> float:
        """
        Advances the simulation clock according to its mode.
        Returns the new simulation time in seconds.
        """
        now_wall = time.time()
        elapsed_wall = now_wall - self.last_tick_wall_time
        
        if self.mode == ClockMode.REALTIME:
            self.current_sim_time += elapsed_wall
        elif self.mode == ClockMode.ACCELERATED:
            self.current_sim_time += elapsed_wall * self.speedup_factor
        elif self.mode == ClockMode.STEP:
            self.current_sim_time += step_size_hours * 3600.0
            
        self.last_tick_wall_time = now_wall
        return self.current_sim_time

    def set_time(self, sim_time: float):
        self.current_sim_time = sim_time
        self.last_tick_wall_time = time.time()
