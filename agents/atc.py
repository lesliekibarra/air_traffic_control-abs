from mesa import Agent
import math
from agents.aircraft import Aircraft
from queue import Queue

class AirTrafficControl(Agent):
    def __init__(self, model, airport_id: str, control_radius_km: int):
        super().__init__(model=model)
        self.airport_id = airport_id
        self.control_radius_km = control_radius_km
        self.aircraft_to_direct = Queue()
        
    def step(self):
        weather = self.model.weather_agent.get_conditions()
        # Iterate over all agents
        for agent in self.model.agents:
            if isinstance(agent, Aircraft):
                if self._in_control_area(agent.position):
                    self.aircraft_to_direct.put(agent)
                    # self._issue_instructions(agent, weather)
    
    def _in_control_area(self, position):
        if position is None:
            return False
        distance = self._haversine((self.model.latitude, self.model.longitude), position)
        return distance <= self.control_radius_km

    def _issue_instructions(self, aircraft, weather):
        if weather.get("visibility") == "Low" or weather.get("precipitation") == "Storm":
            aircraft.status = "Holding"
        elif aircraft.status == "In Flight":
            aircraft.status = "Cleared to Land"
            
    def _haversine(self, coord1, coord2):
            # Calculate great circle distance (in km) between two (lat,lon) points.
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            R = 6371  # Earth radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
