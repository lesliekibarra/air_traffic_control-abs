from mesa import Model
from datetime import datetime, timezone, timedelta
import math
import time
from agents.aircraft import Aircraft, Waypoint
from agents.weather import Weather
from agents.atc import AirTrafficControl
from data_loader import get_flights, get_aircraft_track_path

class AirportATC(Model):
    def __init__(self, airport_id: str, start: datetime, end: datetime):
        super().__init__()
        self.airport_id = airport_id
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        self.start = start
        self.end = end
        self.current_time = start
        self.atc_agent = AirTrafficControl(model=self, airport_id=airport_id)
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
            Aircraft(
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

    def get_airport_location(self, airport_id):
        # Dummy implementation – replace with actual coordinates lookup.
        return (0.0, 0.0)
    
    def haversine(self, coord1, coord2):
        # Calculate great circle distance (in km) between two (lat,lon) points.
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
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

    airport_atc = AirportATC("LAX", start, end)
    airport_atc.run_model()