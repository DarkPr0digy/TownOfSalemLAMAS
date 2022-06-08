from enum import Enum
from Event import Event, EventType


class Role(Enum):
    """
    Enum class for the roles of the agents.
    """
    LO = 0  # Lookout
    Doc = 1  # Doc
    Vet = 2  # Veteran
    Esc = 3  # Escort
    GF = 4  # Godfather
    Vig = 5  # Vigilante
    May = 6  # Mayor


class Agent:
    def __init__(self, role, name):
        self.role = role
        self.will = None
        self.events = []
        self.name = name
        self.is_alive = True
        self.knowledge = {name + "_" + str(role.name): True}

    def __str__(self):
        return str(self.role.name) + ": " + str(self.name)

    def death(self):
        self.is_alive = False

    def get_will(self):
        self.will = "Last will and Testament of " + self.name + "\n"
        self.will += "------------------------------------------------\n"
        self.will += str("I am the " + str(self.role.name) + "\n")
        for event in self.events:
            self.will += str(event) + "\n"

        return self.will, self.role, self.events

    def register_event(self, agent, target, event_type: EventType):
        self.events.append(Event(event_type, agent.name, target.name))

    def vote(self, target, num_votes=1):
        # TODO: I assume mayor can only use their votes on 1 person even if they have 3
        # TODO: Should also return something
        self.register_event(self, target, EventType.Voted)


# region Individual Roles - Where their individual methods will gos
class Lookout(Agent):
    def __init__(self, name):
        self.name = name
        super().__init__(Role.LO, name)

    def observe(self, target, someone_visited: bool, who_visited: [Agent]):
        self.register_event(self, target, EventType.Observed)

        if someone_visited:
            for agent in who_visited:
                self.register_event(agent, target, EventType.Visited)


class Doctor(Agent):
    def __init__(self, name):
        super().__init__(Role.Doc, name)
        self.used_self_heal = False

    def heal(self, target):
        if target == self:
            self.used_self_heal = True
        self.register_event(self, target, EventType.Healed)


class Escort(Agent):
    def __init__(self, name):
        super().__init__(Role.Esc, name)

    def distract(self, target):
        self.register_event(self, target, EventType.Distracted)


class Godfather(Agent):
    def __init__(self, name):
        super().__init__(Role.GF, name)

    def kill(self, target):
        self.register_event(self, target, EventType.Killed)


class Mayor(Agent):
    def __init__(self, name):
        super().__init__(Role.May, name)
        self.is_revealed = False

    def reveal_self(self):
        self.is_revealed = True

    def vote(self, target, num_votes=1):
        # TODO: I assume mayor can only use their votes on 1 person even if they have 3
        # TODO: Should also return something
        self.register_event(self, target, EventType.Voted)


class Veteran(Agent):
    def __init__(self, name):
        super().__init__(Role.Vet, name)
        self.alert = False  # implementation for this
        self.used_alert = 2

    def change_alert(self):
        self.alert = True
        self.used_alert -= 1

    def night_action(self, is_visited, visitors):
        # TODO: I assume they kill all visitors
        if self.alert and is_visited:
            for visitor in visitors:
                self.register_event(self, visitor, EventType.Killed)


class Vigilante(Agent):
    def __init__(self, name):
        super().__init__(Role.Vig, name)

    def kill(self, target):
        self.register_event(self, target, EventType.Killed)


# endregion


if __name__ == "__main__":
    W = Veteran("Bobby Ross")
    V = Agent(Role.Vet, "Bobby Russo")

    print(W.role.name)

    X = Godfather("Don Carlo")
    Y = Mayor("Adam West")
    Z = Lookout(name="Snitch McSnitch")

    X.register_event(X, Y, EventType.Distracted)
    X.register_event(X, Y, EventType.Voted)
    X.register_event(X, Y, EventType.Killed)

    Z.observe(Y, True, [X, Z])

    will, _, _ = X.get_will()
    print(will)
    print("------------------------------------------------\n")
    will, _, _ = Z.get_will()
    print(will)
