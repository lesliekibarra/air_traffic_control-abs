from mesa import Model
from mesa.space import MultiGrid
from datetime import datetime, timezone, timedelta
import math
import time
from typing import Tuple
from agents.aircraft import Aircraft, Waypoint
from agents.weather import Weather
from agents.atc import AirTrafficControl
from data_loader import get_flights, get_aircraft_track_path

class Airport(Model):
    def __init__(self, start: datetime, end: datetime, airport_id: str, gps: Tuple[float, float], control_radius_km: int = 200):
        super().__init__()
        self.airport_id = airport_id
        self.latitude, self.longitude = gps
        self.control_radius_km = control_radius_km
        self.space_width = 100
        self.space_height = 100
        self.space, self.bounds = self._create_airport_ctrl_space()
        
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        self.start = start
        self.end = end
        self.current_time = start
        
        self.atc_agent = AirTrafficControl(model=self, airport_id=airport_id, control_radius_km=control_radius_km)
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
            
            ac_location = self._gps_to_grid(ac.waypoints[0].longitude, ac.waypoints[0].latitude)
            self.space.place_agent(ac, ac_location)
    
    def _create_airport_ctrl_space(self):
        latitude_diff = self.control_radius_km / 111.11 # Approximate conversion from km to degrees latitude
        longitude_diff = self.control_radius_km / (111.11 * math.cos(math.radians(self.latitude))) # Approximate conversion from km to degrees longitude
        
        # Calculate the bounds based on the center and the differences
        bounds = {
            'lon_min': self.longitude - longitude_diff,
            'lon_max': self.longitude + longitude_diff,
            'lat_min': self.latitude - latitude_diff,
            'lat_max': self.latitude + latitude_diff
        }
        
        space = MultiGrid(width=self.space_width, height=self.space_height, torus=False)
        return space, bounds
    
    def _gps_to_grid(self, longitude: float, latitude: float) -> Tuple[int, int]:
        x = int((longitude - self.bounds['lon_min']) / (self.bounds['lon_max'] - self.bounds['lon_min']) * self.space_width)
        y = int((latitude - self.bounds['lat_min']) / (self.bounds['lat_max'] - self.bounds['lat_min']) * self.space_height)
        # Ensure indices are within grid limits
        x = max(0, min(x, self.space_width - 1))
        y = max(0, min(y, self.space_height - 1))
        return x, y
    
    def run_model(self):
        while self.current_time < self.end:
            print(f"Simulation time: {self.current_time}")
            self.agents.do("step")
            self.agents.do("advance")
            time.sleep(1)
            self.current_time += timedelta(minutes=1)

if __name__ == "__main__":
    start = datetime(2025, 3, 1, 14, 0)
    end = datetime(2025, 3, 1, 14, 30)
    airport_id = "LAX"
    gps = (33.942791, -118.410042)

    airport = Airport(start=start, end=end, airport_id=airport_id, gps=gps)
    airport.run_model()