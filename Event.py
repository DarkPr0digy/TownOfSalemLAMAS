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


class EventTypeAtomic(Enum):
    """
    Enum for types of events in the game
    """
    V = 0
    K = 1
    H = 2
    D = 3
    O = 4
    T = 5


class Event:
    def __init__(self, event_type: EventType, agent: str, target: str, day: int):
        self.event_type = event_type
        self.agent = agent
        self.target = target
        self.day = day

    def __str__(self):
        return self.agent + " " + str(self.event_type.name) + " " + self.target + " on day " + str(self.day)
