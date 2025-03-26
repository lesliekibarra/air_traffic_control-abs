from mesa import Agent
from agents.aircraft import Aircraft
from queue import Queue

class AirTrafficControl(Agent):
    def __init__(self, model, airport_id: str, control_radius_km: int = 100):
        super().__init__(model=model)
        self.airport_id = airport_id
        self.control_radius_km = control_radius_km
        self.aircraft_to_direct = Queue()
        
    def step(self):
        weather = self.model.weather_agent.get_conditions()
        # Iterate over all agents
        for agent in self.model.agents:
            if isinstance(agent, Aircraft):
                print(f"ATC: {agent.callsign} is {agent.status}")
                if self._in_control_area(agent.position):
                    print(f"ATC: {agent.callsign} is in control area")
                    self.aircraft_to_direct.put(agent)
                    self._issue_instructions(agent, weather)
    
    def _in_control_area(self, position):
        if position is None:
            return False
        airport_pos = self.model.get_airport_location(self.airport_id)
        return self.model.haversine(position, airport_pos) <= self.control_radius_km

    def _issue_instructions(self, aircraft, weather):
        if weather.get("visibility") == "Low" or weather.get("precipitation") == "Storm":
            aircraft.status = "Holding"
        elif aircraft.status == "In Flight":
            aircraft.status = "Cleared to Land"
