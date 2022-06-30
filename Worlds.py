from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
import copy


class Worlds:
    def __init__(self, agents, roles, ax):
        self.agents = agents
        self.knowledge_dict = {}
        self.axioms = ax
        self.worlds = []
        self.worlds = self.create_worlds(self.worlds, self.knowledge_dict,
                                         self.agents, roles)
        self.kripke_structures = []

    # Create all possible worlds, so all combinations of agents and roles
    def create_worlds(self, worlds, knowledge_dict, agents, roles):
        for x in range(len(agents)):
            agent = agents.pop(0)
            role = roles.pop(x)
            knowledge_dict[self.axioms.get_fact_role(agent, role)] = True
            if bool(agents):
                worlds = self.create_worlds(worlds, knowledge_dict, agents, roles)
            else:
                # Copy the dictionary so it does not get changed:
                c_dict = copy.deepcopy(knowledge_dict)
                worlds.append(World(str(len(worlds) + 1), c_dict))
            del knowledge_dict[self.axioms.get_fact_role(agent, role)]
            agents.insert(0, agent)
            roles.insert(x, role)
        self.worlds = worlds
        return worlds

    # Create the relations for each agent for their accessible worlds
    def create_starting_relations(self, roles, agent):
        relations = agent.relations
        for role in roles:
            connected_worlds = []
            for world in self.worlds:
                if (agent.name + "_" + str(role)) in world.assignment:
                    connected_worlds.append(world)
            # In every connected the agent has the role 'role', so there should be a relation between them
            while bool(connected_worlds):
                c_world = connected_worlds.pop(0)
                # Reflexivity relation to itself
                relations.append((c_world.name, c_world.name))
                for world in connected_worlds:
                    relations.append((c_world.name, world.name))
                    relations.append((world.name, c_world.name))
        agent.relations = relations

    # Create kripke structures
    def create_kripke_structures(self):
        ks_structs = {}
        for agent in self.agents:
            ks_structs[agent.name] = KripkeStructure(self.worlds, agent.relations)
        self.kripke_structures = ks_structs

    # Remove relations to removed worlds
    def remove_relations_removed_worlds(self, removed_worlds, agents):
        for agent in agents:
            relations = agent.relations
            counter = 0
            deleted_relations = []
            for relation in relations:
                for removed_world in removed_worlds:
                    if relation[0] == removed_world.name or relation[1] == removed_world.name:
                        deleted_relations.append(counter)
                        break
                counter += 1
            counter = 0
            for del_rela in deleted_relations:
                del agent.relations[del_rela - counter]
                counter += 1

    def public_announcement(self, fact):
        # In a public announcement, everyone knows that everyone knows that 'fact' is true, and everyone knows
        # that everyone knows that worlds where 'fact' is false is not a feasible world, so remove all worlds
        # where 'fact' is false and remove all relations to the removed worlds
        for agent in self.agents:
            agent.add_fact(fact)
        # If one of the facts is about a role of a different player:
        # Everyone knows that everyone knows that the role was revealed so
        # Remove worlds where that fact is not in the world assignment
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            removed_worlds = self.remove_worlds(fact)
            self.remove_relations_removed_worlds(removed_worlds, self.agents)

    # Removes worlds that have fact == False from the list
    def remove_worlds(self, fact):
        removed_worlds = []
        for world in self.worlds:
            if fact not in world.assignment:
                removed_worlds.append(world)
        for removed_world in removed_worlds:
            self.worlds.remove(removed_world)
        return removed_worlds

    # Removes worlds that have no relations to it
    def remove_redundant_worlds(self):
        check = 1
        removed_worlds = []
        for world in self.worlds:
            for agent in self.agents:
                check = 0
                for rel in agent.relations:
                    if rel[0] == world.name or rel[1] == world.name:
                        check = 1
                        break
                if check == 1:
                    break
            if check == 0:
                removed_worlds.append(world)
        for removed_world in removed_worlds:
            self.worlds.remove(removed_world)
