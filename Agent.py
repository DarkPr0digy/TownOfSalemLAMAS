from enum import Enum


class Role(enum):
    """
    Enum class for the roles of the agents.
    """
    Lookout = 0
    Doctor = 1
    Veteran = 2
    Escort = 3
    Godfather = 4
    Vigilante = 5
    Mayor = 6


class Agent():
    def __init__(self, role):
        self.role = role
