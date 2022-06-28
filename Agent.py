import itertools
import random
from enum import Enum
from Event import Event, EventType, EventTypeAtomic
from Worlds import *
import sys, os

# TODO: RANDOMIZER FOR AGENT SELECTION (80 knowledge | 20 random)
# TODO: KNOWLEDGE GENERATION THING ~~~~

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


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
    Maf = 7  # Mafioso


class Agent:
    def __init__(self, role, name):
        self.role = role
        self.will = None
        self.events = []
        self.name = name
        self.is_alive = True
        self.is_mafia = False

        # Two seperate knowledge banks for faster execution
        # Theoretically they can be represented in one
        self.knowledge = []
        self.neg_knowledge = []

        self.knowledge.append(name + "_" + str(role.name))
        self.is_being_healed = False
        self.relations = []
        self.will_read = False

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

        return self.will

    def add_fact(self, fact):
        if fact not in self.knowledge:
            self.knowledge.append(fact)

    def add_neg_fact(self, fact):
        if fact not in self.neg_knowledge:
            self.neg_knowledge.append(fact)

    def infer_facts(self, ax):
        information_gained = True
        max_iterations = 0
        while information_gained:
            inf_facts = []
            # General axioms
            # Axiom 1: needs 1 fact only:
            for fact in self.knowledge:
                for f in ax.axiom_1(fact, self):
                    inf_facts.append(f)

            # Axiom 2A: needs negative facts with the same role
            if len(self.neg_knowledge) > 3:
                facts = []
                # For every role, check if there are 4 negative agent facts
                for role in Role:
                    for fact in self.neg_knowledge:
                        if fact[6:] == str(role.name):
                            if fact not in facts:
                                facts.append(fact)
                    # If there are 4, we can infer the role of an agent
                    if len(facts) == 4:
                        for f in ax.axiom_2A(facts):
                            inf_facts.append(f)
                    facts = []

            # Axiom 2B: needs negative facts for the same agent
            if len(self.neg_knowledge) > 3:
                facts = []
                # For every agent, check if there are 4 negative role facts
                for x in range(1,6):
                    for fact in self.neg_knowledge:
                        if fact[4] == str(x):
                            if fact not in facts:
                                facts.append(fact)
                    # If there are 4, we can infer the role of the agent
                    if len(facts) == 4:
                        for f in ax.axiom_2B(facts, Role):
                            inf_facts.append(f)
                    facts = []

            if self.role.name == 'LOO':
                # Axiom 3: needs 3 facts:
                for facts in list(itertools.permutations(self.knowledge, 3)):
                    for f in ax.axiom_3(facts):
                        inf_facts.append(f)

                # Axiom 4: needs 2 facts
                for facts in list(itertools.permutations(self.knowledge, 2)):
                    for f in ax.axiom_4(facts):
                        inf_facts.append(f)

                # Axiom 5: needs 3 facts
                for facts in list(itertools.permutations(self.knowledge, 3)):
                    for f in ax.axiom_5(facts, self.knowledge):
                        inf_facts.append(f)

                # Axiom 6: needs 3 facts
                for facts in list(itertools.permutations(self.knowledge, 3)):
                    for f in ax.axiom_6(facts):
                        inf_facts.append(f)

            # Axiom 7 is only for the doctor
            if self.role.name == 'Doc' and False:
                # Axiom 7: needs 4 facts
                for facts in list(itertools.permutations(self.knowledge, 4)):
                    for f in ax.axiom_7(facts):
                        inf_facts.append(f)

            for fact in inf_facts:
                if fact not in self.knowledge or fact not in self.neg_knowledge:
                    information_gained = True
                    break
                else:
                    information_gained = False

            # Check if no facts are added or max iterations reaches 10
            if len(inf_facts) == 0 or max_iterations > 10:
                information_gained = False
            else:
                max_iterations += 1
                for fact in inf_facts:
                    if fact[0:3] == 'not':
                        self.add_neg_fact(fact)
                    else:
                        self.add_fact(fact)
                inf_facts = []

    def update_relations(self, worlds, ax):
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
        # self.knowledge.append(agent.name + str(EventTypeAtomic(event_type.value).name) + target.name + "_N" + str(day))

    def vote(self, target, day):
        self.register_event(self, target, EventType.Voted, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_D" + str(day))
        return target, 1

    def determine_my_knowledge(self, worlds, living_agents, living_roles):
        """
        Method to determine the knowledge of the given agent regarding the role of other agents - First order knowledge
        :param worlds: The set of worlds
        :param living_agents: The set of living agents
        :param living_roles: The set of living roles
        :return: a dictionary with our knowledge of the roles of the other agents
        """
        # relations = {'a': {('1', '2')}, 'b': {}} - format needed
        agents = living_agents
        roles = living_roles

        # Generate Combinations of living roles and agents
        agent_combinations = []

        for comb in itertools.product(agents, roles):
            agent_combinations.append(comb[0] + "_" + comb[1])

        items_to_remove = []

        for x in range(len(agent_combinations)):
            if agent_combinations[x].split("_")[0] == self.name:
                items_to_remove.append(agent_combinations[x])

        for items in items_to_remove:
            if items in agent_combinations:
                agent_combinations.remove(items)

        # Get agents relations
        relations = {}
        relations[self.name] = set(self.relations)

        # See if in all worlds an agent knows this to be true
        ks = KripkeStructure(worlds, relations)
        results = []
        for roles in agent_combinations:
            form = Box_a(self.name, Atom(roles))
            world_results = []
            for world in worlds:
                world_results.append(form.semantic(ks, world.name))
            results.append(world_results)

        for x in range(len(results)):
            if all(results[x]):
                results[x] = True
            else:
                results[x] = False

        knowledge = {}
        for possible_roles, result in zip(agent_combinations, results):
            knowledge[possible_roles] = result

        return knowledge

    def determine_possibilities(self, worlds, living_agents, living_roles):
        """
        Method to determine the knowledge of the given agent regarding the possible role of other agents
        :param worlds: The set of worlds
        :param living_agents: The set of living agents
        :param living_roles: The set of living roles
        :return: a dictionary with our knowledge of the possible roles of the other agents
        """
        # relations = {'a': {('1', '2')}, 'b': {}} - format needed
        agents = living_agents
        roles = living_roles

        # Generate Combinations of living roles and agents
        agent_combinations = []

        for comb in itertools.product(agents, roles):
            agent_combinations.append(comb[0] + "_" + comb[1])

        agent_combinations.remove(self.name + "_" + self.role.name)

        # Get agents relations
        relations = {}
        relations[self.name] = set(self.relations)

        # See if in all worlds an agent knows this to be true
        ks = KripkeStructure(worlds, relations)
        results = []
        for roles in agent_combinations:
            if roles != self.name + "_" + self.role.name:
                form = Diamond_a(self.name, Atom(roles))
                world_results = []
                for world in worlds:
                    world_results.append(form.semantic(ks, world.name))
                results.append(world_results)

        # print("Agent Combinations: ", agent_combinations)
        # for x in range(len(results)):
        #     print("World Proposition (", agent_combinations[x], ") World Number", x + 1, ": ", results[x])

        for x in range(len(results)):
            if sum(results[x]) >= 1:
                results[x] = True
            else:
                results[x] = False

        possibilities = {}
        for possible_roles, result in zip(agent_combinations, results):
            possibilities[possible_roles] = result

        return possibilities

    def determine_who_could_be_mafia(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine who could be a mafia member
        :param worlds: The set of worlds
        :param living_agents: The set of living agents
        :param living_roles: The set of living roles
        :return: a dictionary with our knowledge of the possible roles of the other agents
        """
        possibilities = self.determine_possibilities(worlds, living_agents, living_roles)

        could_be_mafia = []

        for key in possibilities.keys():
            agent_name = key.split("_")[0]
            agent_possible_role = key.split("_")[1]
            if agent_possible_role == "GFR" and possibilities[key]:
                could_be_mafia.append(agent_name)

        for x in range(len(could_be_mafia)):
            for agent in agents:
                if could_be_mafia[x] == agent.name:
                    could_be_mafia[x] = agent
                    break

        return could_be_mafia

    def determine_other_agents_knowledge_about_me(self, agents, worlds):
        """
        Method to determine if the other agents know a given agents role - Second Order Knowledge - do I know they know
        :param agents: The set of agents in the game
        :param worlds: the set of worlds in the game
        :return: dictionary that tells whether other living agents know given agents role
        """
        my_true_role = self.name + "_" + self.role.name

        # Get all living agents relations
        relations = {}

        for agent in agents:
            if agent.is_alive:
                relations[agent.name] = set(agent.relations)

        # Determine whether the agents know this agents role in all worlds
        ks = KripkeStructure(worlds, relations)

        results = []
        agents_that_know = []
        for agent in agents:
            if agent.is_alive and agent is not self:
                agents_that_know.append(agent.name)
                formula = Box_a(self.name, Box_a(agent.name, Atom(my_true_role)))

                world_results = []
                for world in worlds:
                    world_results.append(formula.semantic(ks, world.name))
                results.append(world_results)

        for x in range(len(results)):
            if all(results[x]):
                results[x] = True
            else:
                results[x] = False

        knowledge = {}
        for agent, results in zip(agents_that_know, results):
            knowledge[agent] = results

        return knowledge

    def determine_who_to_vote_for(self, worlds, living_agents, living_roles):
        """
        Method to determine who should be voted for
        :param worlds: The set of worlds
        :param living_agents: The set of living agents
        :param living_roles: The set of living roles
        :return: the name of the agent to vote for
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)
        vote = []
        if self.is_mafia:
            # None is Abstain
            for key in knowledge.keys():
                if (key.split("_")[1] != "GFR" or key.split("_")[1] != "Maf") and knowledge[key] is True:
                    vote.append(key)
        else:
            # Select Mafia if you know who they are
            for key in knowledge.keys():
                if (key.split("_")[1] == "GFR" or key.split("_")[1] == "Maf") and knowledge[key] is True:
                    vote.append(key)

        # Convert Vote to Actual Agent Names
        for x in range(len(vote)):
            vote[x] = vote[x].split("_")[0]

        if len(vote) == 0:
            return None
        else:
            return vote[random.randint(0, len(vote) - 1)]

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Generalized method to determine which agent the ability should be used on
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        living = [x for x in agents if x.is_alive]
        living.remove(self)
        return living[random.randint(0, len(living) - 1)]


# region Individual Roles
# region Town
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
                self.knowledge.append(
                    agent.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine which agent the lookout should observed
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)

        agents_to_be_watched = []
        for keys in knowledge.keys():
            if (keys.split("_")[1] != "GFR") and keys.split("_")[0] != self.name and knowledge[keys]:
                # It is not a Mafia member therefore you should watch
                agents_to_be_watched.append(keys)

        living = [x for x in agents if x.is_alive]
        living.remove(self)

        if len(agents_to_be_watched) > 0:
            target = agents_to_be_watched[random.randint(0, len(agents_to_be_watched) - 1)]

            for agent in living:
                if agent.name == target.split("_")[0]:
                    target = agent
                    return target
        else:
            target = living[random.randint(0, len(living) - 1)]
            return target


class Doctor(Agent):
    def __init__(self, name):
        super().__init__(Role.Doc, name)

    def heal(self, target, day):
        self.register_event(self, target, EventType.Healed, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine which agent the doctor should heal
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)
        agents_to_be_healed = []
        for keys in knowledge.keys():
            if keys.split("_")[1] != "GFR" and keys.split("_")[0] != self.name and knowledge[keys]:
                # It is not a Mafia member or you therefore you should heal
                agents_to_be_healed.append(keys)

        living = [x for x in agents if x.is_alive]
        living.remove(self)

        if len(agents_to_be_healed) > 0:
            target = agents_to_be_healed[random.randint(0, len(agents_to_be_healed) - 1)]

            for agent in living:
                if agent.name == target.split("_")[0]:
                    target = agent
                    return target
        else:
            target = living[random.randint(0, len(living) - 1)]
            return target


class Escort(Agent):
    def __init__(self, name):
        super().__init__(Role.Esc, name)

    def distract(self, target, day):
        self.register_event(self, target, EventType.Distracted, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Distracted.value).name) + target.name + "_N" + str(day))

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine which agent the Escort should distract
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)

        agents_to_be_distracted = []
        for keys in knowledge.keys():
            if (keys.split("_")[1] == "GFR" or keys.split("_")[1] == "Maf") and keys.split("_")[0] != self.name and knowledge[keys]:
                # It is a Mafia member therefore you should distract
                agents_to_be_distracted.append(keys)

        living = [x for x in agents if x.is_alive]
        living.remove(self)

        if len(agents_to_be_distracted) != 0:
            target = agents_to_be_distracted[random.randint(0, len(agents_to_be_distracted) - 1)]

            print(target)
            for agent in living:
                if agent.name == target.split("_")[0]:
                    target = agent
                    break

            return target
        else:

            return living[random.randint(0, len(living) - 1)]


class Mayor(Agent):
    def __init__(self, name):
        super().__init__(Role.May, name)
        self.is_revealed = False
        self.has_announced = False
        self.num_revealed_votes = 3

    def determine_reveal_self(self, worlds, living_agents, living_roles):
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)

        for keys in knowledge.keys():
            if keys.split("_")[1] == "GFR" and keys.split("_")[0] != self.name and knowledge[keys]:
                # I know who the mafia is
                self.is_revealed = True
                break

    def reveal_self(self):
        print("[INFO] Mayor is revealing self")
        self.has_announced = True

    def vote(self, target, day):
        if self.is_revealed:
            for i in range(self.num_revealed_votes):
                self.register_event(self, target, EventType.Voted, day)
                self.knowledge.append(
                    self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_D" + str(day))
                return target, self.num_revealed_votes
        else:
            self.register_event(self, target, EventType.Voted, day)
            self.knowledge.append(
                self.name + str(EventTypeAtomic(EventType.Voted.value).name) + target.name + "_D" + str(day))
            return target, 1


class Veteran(Agent):
    def __init__(self, name):
        super().__init__(Role.Vet, name)
        self.alert = False  # implementation for this
        self.used_alert = 2

    def change_alert(self):
        self.alert = True
        self.used_alert -= 1

    # TODO: Could be smarter?? - based on knowledge
    def decide_go_active(self, living_agents):
        alert_probability = random.random()
        if alert_probability < 1 / (len(living_agents) - 1):
            if self.used_alert >= 1:
                self.change_alert()
                print("[INFO] Vet Is Going Active")

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
        self.killed_correctly = None

    def kill(self, target, day):
        self.register_event(self, target, EventType.Killed, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Killed.value).name) + target.name + "_N" + str(day))

        target.death()

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine which agent the Godfather should kill
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)
        agents_to_target = []
        for keys in knowledge.keys():
            if (keys.split("_")[1] == "GFR" or keys.split("_")[1] == "Maf") and knowledge[keys]:
                # It is a Mafia member therefore you should kill
                agents_to_target.append(keys)

        living = [x for x in agents if x.is_alive]
        living.remove(self)

        if len(agents_to_target) != 0:
            target = agents_to_target[random.randint(0, len(agents_to_target) - 1)]

            for agent in living:
                if agent.name == target.split("_")[0]:
                    target = agent
                    break
            return target
        else:
            return None

# endregion

# region Mafia
class Godfather(Agent):
    def __init__(self, name):
        super().__init__(Role.GFR, name)
        self.is_mafia = True

    def kill(self, target, day):
        self.register_event(self, target, EventType.Killed, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))
        target.death()

    def determine_who_to_use_ability_on(self, worlds, living_agents, living_roles, agents):
        """
        Method to determine which agent the lookout should observed
        :param worlds: the set of worlds
        :param living_agents: the set of living agents
        :param living_roles: the set of living roles
        :return: The name of the agent to use ability on
        """
        knowledge = self.determine_my_knowledge(worlds, living_agents, living_roles)
        agents_to_be_target = []
        for keys in knowledge.keys():
            if keys.split("_")[0] != self.name and knowledge[keys]:
                # It is not a Mafia member therefore you should kill
                agents_to_be_target.append(keys)

        living = [x for x in agents if x.is_alive]
        living.remove(self)

        if len(agents_to_be_target) > 0:
            target = agents_to_be_target[random.randint(0, len(agents_to_be_target) - 1)]

            for agent in living:
                if agent.name == target.split("_")[0]:
                    target = agent
                    return target
        else:
            # Godfather knows who Mafia is thus remove them from potential targets
            for agent in living:
                if agent.role.name == "Maf":
                    living.remove(agent)
            target = living[random.randint(0, len(living) - 1)]
            return target



class Mafioso(Agent):
    def __init__(self, name):
        super().__init__(Role.Maf, name)
        self.is_mafia = True

    def kill(self, target, day):
        self.register_event(self, target, EventType.Killed, day)
        self.knowledge.append(
            self.name + str(EventTypeAtomic(EventType.Visited.value).name) + target.name + "_N" + str(day))
        target.death()


# endregion
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

    will = X.get_will()
    print(will)
    print("------------------------------------------------\n")
    will = Z.get_will()
    print(will)
