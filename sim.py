import threading
from datetime import datetime

from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component
)

from airport import Airport
from agents.aircraft import Aircraft

def aircraft_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    if isinstance(agent, Aircraft):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Color"] = "#1f77b4"
        portrayal["Filled"] = "true"
        portrayal["x"] = agent.position[0]
        portrayal["y"] = agent.position[1]
        portrayal["text"] = agent.callsign
        portrayal["text_color"] = "#ffffff"
        
    return portrayal

start = datetime(2025, 3, 1, 14, 0)
end = datetime(2025, 3, 1, 14, 15)
airport_id = "LAX"
gps = (33.942791, -118.410042)

model_params = { 
    "start": start,
    "end": end,
    "airport_id": airport_id,
    "gps": gps
}

airport = Airport(start=start, end=end, airport_id=airport_id, gps=gps)
airport.run_model()

space_component = make_space_component(portrayal_moethod=aircraft_portrayal, canvas_height=500, canvas_width=500)

page = SolaraViz(
    airport,
    components=[
        space_component
    ],
    model_params=model_params,
    name="Airport Simulation"
)

page

sim_thread = threading.Thread(target=airport.run_model, daemon=True)
sim_thread.start()