import itertools
from enum import Enum
from Event import Event, EventType, EventTypeAtomic

from TownOfSalemLAMAS.Axiom import Axiom

class Role(Enum):
    """
    Enum class for the roles of the agents.
    """
    LOO = 0  # Lookout
    Doc = 1  # Doc
    Vet = 2  # Veteran
    Esc = 3  # Escort
    GFR = 4  # Godfather
    Vig = 5  # Vigilante
    May = 6  # Mayor


class Agent:
    def __init__(self, role, name):
        self.role = role
        self.will = None
        self.events = []
        self.name = name
        self.is_alive = True
        # self.knowledge = {name + "_" + str(role.name): True}
        self.knowledge = []
        self.knowledge.append(name + "_" + str(role.name))
        self.is_being_healed = False
        self.relations = []

    def __str__(self):
        return str(self.role.name) + ": " + str(self.name)

    def death(self):
        if not self.is_being_healed:
            self.is_alive = False

    def get_will(self):
        # TODO: Add how they died to the will
        self.will = "Last will and Testament of " + self.name + "\n"
        self.will += "------------------------------------------------\n"
        self.will += str("I am the " + str(self.role.name) + "\n")
        for event in self.events:
            self.will += str(event) + "\n"

        return self.will, self.role, self.events

    def add_fact(self, fact):
        if fact not in self.knowledge:
            self.knowledge.append(fact)

    # Implement this function
    def infer_facts(self):
        ax = Axiom()
        information_gained = True
        max_iterations = 0
        while information_gained:
            inf_facts = []
            # Axiom 1: needs 1 fact only:
            # for fact in self.knowledge:
                # for f in ax.axiom_1(fact, self):
                    # inf_facts.append(f)

            if self.role.name == 'LOO':
                # Axiom 3: needs 3 facts:
                for facts in list(itertools.permutations(self.knowledge, 3)):
                    for f in ax.axiom_3(facts):
                        inf_facts.append(f)

                # Axiom 4: needs 3 facts
                for facts in list(itertools.permutations(self.knowledge, 2)):
                    for f in ax.axiom_4(facts, self.knowledge):
                        inf_facts.append(f)

            # Axiom 5: needs 2 facts bla bla

            # Check if no facts are added or max iterations reaches 10
            if len(inf_facts) == 0 and max_iterations < 10:
                information_gained = False
            else:
                max_iterations += 1
                for fact in inf_facts:
                    self.knowledge.append(fact)

    def update_relations(self, worlds):
        ax = Axiom()
        accessible_worlds = []
        removed_worlds = []
        for rel in self.relations:
            if rel[0] not in accessible_worlds:
                accessible_worlds.append(rel[0])
            if rel[1] not in accessible_worlds:
                accessible_worlds.append(rel[1])
        for world in worlds:
            if world.name in accessible_worlds:
                for fact in self.knowledge:
                    if ax.check_fact_is_role(fact):
                        if fact not in world.assignment and world.name not in removed_worlds:
                            removed_worlds.append(world.name)
        for world in removed_worlds:
            accessible_worlds.remove(str(world))
        removed_relations = []
        for rel in self.relations:
            if rel[0] not in accessible_worlds or rel[1] not in accessible_worlds:
                removed_relations.append(rel)
        for relation in removed_relations:
            self.relations.remove(relation)

    def discover_role(self, target, role):
        self.knowledge.append(target.name + "_" + str(role.name))

    def register_event(self, agent, target, event_type: EventType, day: int):
        self.events.append(Event(event_type, agent.name, target.name, day))
        #self.knowledge.append(agent.name + str(EventTypeAtomic(event_type.value).name) + target.name + "_N" + str(day))

    def vote(self, target, day, num_votes=1):
        # TODO: I assume mayor can only use their votes on 1 person even if they have 3
        # TODO: Should also return something
        self.register_event(self, target, EventType.Voted, day)
        self.knowledge.append(self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_N"+str(day))


# region Individual Roles - Where their individual methods will go
class Lookout(Agent):
    def __init__(self, name):
        super().__init__(Role.LOO, name)
        self.name = name

    def observe(self, target, someone_visited: bool, who_visited: [Agent], day):
        self.register_event(self, target, EventType.Observed, day)
        # TODO: Ignore that I observed them?
        # self.knowledge[agent.name + "_" + str(EventTypeAtomic(event_type.value).name) + "_" + target.name] = True

        if someone_visited:
            for agent in who_visited:
                self.register_event(agent, target, EventType.Visited, day)
                self.knowledge.append(agent.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))


class Doctor(Agent):
    def __init__(self, name):
        super().__init__(Role.Doc, name)

    def heal(self, target, day):
        self.register_event(self, target, EventType.Healed, day)
        self.knowledge.append(self.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))


class Escort(Agent):
    def __init__(self, name):
        super().__init__(Role.Esc, name)

    def distract(self, target, day):
        self.register_event(self, target, EventType.Distracted, day)
        self.knowledge.append(self.name + str(EventTypeAtomic(EventType.Distracted.value).name) + target.name + "_N" + str(day))


class Godfather(Agent):
    def __init__(self, name):
        super().__init__(Role.GFR, name)

    def kill(self, target, day):
        self.register_event(self, target, EventType.Killed, day)
        self.knowledge.append(self.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))
        target.death()


class Mayor(Agent):
    def __init__(self, name):
        super().__init__(Role.May, name)
        self.is_revealed = False
        self.num_revealed_votes = 3

    def reveal_self(self):
        self.is_revealed = True

    def vote(self, target, day, num_votes=1):
        if self.is_revealed:
            for i in range(self.num_revealed_votes):
                self.register_event(self, target, EventType.Voted, day)
                self.knowledge.append(
                    self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_N" + str(day))

        else:
            self.register_event(self, target, EventType.Voted, day)
            self.knowledge.append(
                self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_N" + str(day))
        # TODO: Return num votes and target??


class Veteran(Agent):
    def __init__(self, name):
        super().__init__(Role.Vet, name)
        self.alert = False  # implementation for this
        self.used_alert = 2

    def change_alert(self):
        self.alert = True
        self.used_alert -= 1

    def night_action(self, is_visited, visitors, day):
        if self.alert and is_visited:
            for visitor in visitors:
                self.register_event(self, visitor, EventType.Killed, day)
                self.knowledge.append(
                    self.name + str(EventTypeAtomic(EventType.Killed.value).name) + visitor.name + "_N" + str(day))

                visitor.death()


class Vigilante(Agent):
    def __init__(self, name):
        super().__init__(Role.Vig, name)

    def kill(self, target, day):
        self.register_event(self, target, EventType.Killed, day)
        self.knowledge.append(self.name + str(EventTypeAtomic(EventType.Killed.value).name) + target.name + "_N" + str(day))

        target.death()


# endregion


if __name__ == "__main__":
    W = Veteran("Bobby Ross")
    V = Agent(Role.Vet, "Bobby Russo")

    X = Godfather("Don Carlo")
    Y = Mayor("Adam West")
    Z = Lookout(name="Snitch McSnitch")

    print(W.role.name)
    print(X.role.value)
    print(EventType.Killed.value)
    print(EventTypeAtomic(EventType.Killed.value).name)
    print(W.knowledge)
    print(V.knowledge)

    X.register_event(X, Y, EventType.Distracted, 1)
    X.register_event(X, Y, EventType.Voted, 1)
    X.register_event(X, Y, EventType.Killed, 1)

    Z.observe(Y, False, [], 1)

    will, _, _ = X.get_will()
    print(will)
    print("------------------------------------------------\n")
    will, _, _ = Z.get_will()
    print(will)
