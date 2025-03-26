from opensky_api import OpenSkyApi
from datetime import datetime, timezone

api = OpenSkyApi()

def to_unix(dt: datetime) -> int:
    """Convert timezone-aware datetime to Unix timestamp (UTC seconds since epoch)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def from_unix(timestamp: int) -> datetime:
    """Convert Unix timestamp to timezone-aware UTC datetime."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def get_flights(airport: str, start: int, end: int, type: str="arrival"):
    start = to_unix(start)
    end = to_unix(end)
    
    flights = []
    if type == "arrival":
        flights = api.get_arrivals_by_airport(airport, start, end)
    elif type == "departure":
        flights = api.get_departures_by_airport(airport, start, end)
    elif type == "all":
        flights = []
        flights.extend(api.get_arrivals_by_airport(airport, start, end))
        flights.extend(api.get_departures_by_airport(airport, start, end))
    else:
        raise ValueError("Invalid type")
    
    return flights
    
def get_aircraft_track_path(uid: str, timestamp: int=None):
    if timestamp is None:
        timestamp = 0
        
    track = api.get_track_by_aircraft(uid, timestamp)

    if track is None:
        raise ValueError("No track found")
    
    return track
