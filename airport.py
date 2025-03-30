from mesa import Model
from mesa.space import ContinuousSpace
from datetime import datetime, timezone, timedelta
import math
import time
from typing import Tuple
from agents.aircraft import Aircraft, Waypoint
from agents.weather import Weather
from agents.atc import AirTrafficControl
from data_loader import get_flights, get_aircraft_track_path

class Airport(Model):
    def __init__(self, start: datetime, end: datetime, airport_id: str, gps: Tuple[float, float]):
        super().__init__()
        self.airport_id = airport_id
        self.latitude, self.longitude = gps
        self.control_radius_km = 100
        self.space = self._create_airport_ctrl_space()
        
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        self.start = start
        self.end = end
        self.current_time = start
        
        self.atc_agent = AirTrafficControl(model=self, control_radius_km=self.control_radius_km)
        self.weather_agent = Weather(model=self)
        
        arrivals = get_flights(f'K{self.airport_id}', start, end, type="arrival")
        print(f"Found {len(arrivals)} arrivals")
        
        for flight in arrivals:
            uid = flight.icao24
            arrival_airport = flight.estArrivalAirport
            departure_airport = flight.estDepartureAirport  
            arrival_time = flight.lastSeen
            departure_time = flight.firstSeen
            
            track = get_aircraft_track_path(uid, timestamp=departure_time)
            waypoints = [
                Waypoint(time=w[0], latitude=w[1], longitude=w[2], altitude=w[3],
                         true_track=w[4], on_ground=w[5])
                for w in track.path
            ]
            ac = Aircraft(
                model=self,
                uid=uid,
                callsign=flight.callsign,
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_time=departure_time,
                arrival_time=arrival_time,
                track_start=track.startTime,
                track_end=track.endTime,
                waypoints=waypoints
            )
    
    def _create_airport_ctrl_space(self):
        space = ContinuousSpace(x_max=-116, y_max=36, x_min=-122, y_min=32, torus=True)

        return space
    
    
    def run_model(self):
        while self.current_time < self.end:
            print(f"Simulation time: {self.current_time}")
            self.agents.do("step")
            self.agents.do("advance")
            time.sleep(1)
            self.current_time += timedelta(seconds=10)

if __name__ == "__main__":
    start = datetime(2025, 3, 1, 14, 0)
    end = datetime(2025, 3, 1, 14, 30)
    airport_id = "LAX"
    gps = (33.942791, -118.410042)

    airport = Airport(start=start, end=end, airport_id=airport_id, gps=gps)
    airport.run_model()