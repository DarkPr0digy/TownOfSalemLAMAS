from enum import Enum


class EventType(Enum):
    """
    Enum for types of events in the game
    """
    Visited = 0
    Killed = 1
    Healed = 2
    Distracted = 3
    Observed = 4
    Voted = 5


class Event:
    def __init__(self, event_type: EventType, agent: str, target: str):
        self.event_type = event_type
        self.agent = agent
        self.target = target

    def __str__(self):
        return self.agent + " " + str(self.event_type.name) + " " + self.target
