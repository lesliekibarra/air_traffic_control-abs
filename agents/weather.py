import random
from mesa import Agent, Model

class Weather(Agent):
    def __init__(self, model: Model):
        super().__init__(model=model)
        self.conditions = {}
        
    def step(self):
        self.conditions['visibility'] = random.choices(["Clear", "Moderate", "Low"], weights=[70, 20, 10])[0]
        self.conditions['wind_speed'] = round(max(0, random.gauss(10, 5)), 1)
        self.conditions['precipitation'] = random.choices(["None", "Light Raain", "Storm"], weights=[85, 10, 5])[0]
        self.conditions['temperature'] = round(random.gauss(20, 5), 1)
        self.conditions['clouds'] = random.choices(["Clear", "Partly Cloudy", "Overcast"], weights=[60, 30, 10])[0]
        
    def get_conditions(self):
        return self.conditions