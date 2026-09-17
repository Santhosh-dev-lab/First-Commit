class StressModel:
    def calculate_modifier(self, temp_c: float, moisture_percent: float) -> float:
        modifier = 1.0
        if temp_c > 35.0:
            modifier *= 0.5
        elif temp_c < 10.0:
            modifier *= 0.2
            
        if moisture_percent < 20.0:
            modifier *= 0.3
        elif moisture_percent > 90.0:
            modifier *= 0.8
            
        return modifier
