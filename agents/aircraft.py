from mesa import Agent
from datetime import datetime, timezone

class Waypoint:
    def __init__(self, time: int, latitude: float, longitude: float, altitude: float, true_track: float, on_ground: bool):
        self.time = datetime.fromtimestamp(time, tz=timezone.utc)
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.true_track = true_track
        self.on_ground = on_ground

class Aircraft(Agent):
    def __init__(self,
                 model,
                 uid: str,
                 callsign: str, 
                 departure_airport: str, 
                 arrival_airport: str, 
                 departure_time: int, 
                 arrival_time: int, 
                 track_start: int, 
                 track_end: int, 
                 waypoints):
        super().__init__(model=model)
        self.unique_id = uid
        self.callsign = callsign
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.track_start = track_start
        self.track_end = track_end
        self.waypoints = waypoints
        self.status = "Scheduled"
        self.curr_waypoint_idx = 0
        self.position = None
        self.altitude = None
    
    def step(self):
        print(f"Aircraft {self.callsign}: {self.status} at {self.model.current_time}")
        print(f"Position: {self.position}, Altitude: {self.altitude}")
        
        if not self.waypoints:
            self.status = "No track"
            return
        
        while self.curr_waypoint_idx < len(self.waypoints):
            point = self.waypoints[self.curr_waypoint_idx]
            if point.time > self.model.current_time:
                break
            self.position = (point.latitude, point.longitude)
            
            self.altitude = point.altitude or 0
            self.curr_waypoint_idx += 1
            
        if self.curr_waypoint_idx >= len(self.waypoints):
            self.status = "Landed"
        else:
            self.status = "In Flight"