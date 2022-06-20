from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

from TownOfSalemLAMAS.Axioms import Axioms


class Worlds:
    def __init__(self, agents, roles):
        self.agents = agents
        self.axioms = Axioms()
        self.knowledge_dict = {}
        self.worlds = []
        self.worlds = self.create_worlds(self.worlds, self.knowledge_dict,
                                         self.agents, roles)
        self.kripke_structures = self.create_kripke_structures()

    def create_worlds(self, worlds, knowledge_dict, agents, roles):
        for x in range(len(agents)):
            agent = agents.pop(0)
            role = roles.pop(x)
            knowledge_dict[self.axioms.get_fact_role(agent, role)] = True
            if bool(agents):
                worlds = self.create_worlds(worlds, knowledge_dict, agents, roles)
            else:
                # Copy the dictionary so it does not get changed:
                c_dict = knowledge_dict.copy()
                worlds.append(World(str(len(worlds) + 1), c_dict))
            del knowledge_dict[self.axioms.get_fact_role(agent, role)]
            agents.insert(0, agent)
            roles.insert(x, role)
        self.worlds = worlds
        return worlds

    # Finished
    def create_starting_relations(self, roles, agent):
        # This function can be changed to make it so that you give
        # the name of the agent and it fetches the relations for that particular agent
        relations = agent.relations
        for role in roles:
            connected_worlds = []
            for world in self.worlds:
                if (agent.name + "_" + str(role)) in world.assignment:
                    connected_worlds.append(world)
            # In every connected the agent has the role 'role', so there should be a relation between them
            while bool(connected_worlds):
                c_world = connected_worlds.pop(0)
                for world in connected_worlds:
                    # Assume reflexivity
                    relations.append((c_world.name, c_world.name))
                    relations.append((world.name, world.name))
                    # Assume the other one
                    relations.append((c_world.name, world.name))
                    relations.append((world.name, c_world.name))
                    # Add something for transitivity
        agent.relations = relations

    # Finished
    def create_kripke_structures(self):
        ks_structs = {}
        for agent in self.agents:
            ks_structs[agent.name] = KripkeStructure(self.worlds, agent.relations)
        self.kripke_structures = ks_structs

    # Finished (is for removing relations to non-existing worlds)
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
                del agent.relations[del_rela-counter]
                counter += 1

    def public_announcent(self, fact):
        # In a public announcement, everyone knows that everyone knows that 'fact' is true, and everyone knows
        # that everyone knows that worlds where 'fact' is false is not a feasible world, so remove all worlds
        # where 'fact' is false and remove all relations to the removed worlds
        removed_worlds = self.remove_worlds(self.worlds, fact)
        self.remove_relations_removed_worlds(removed_worlds, self.agents)

    def remove_worlds(self, worlds, fact):
        removed_worlds = []
        for world in worlds:
            if fact not in world.assignment:
                removed_worlds.append(world)
        for removed_world in removed_worlds:
            worlds.remove(removed_world)
        return removed_worlds

    def remove_conflicting_worlds(self, test_worlds, fact):
        new_worlds = []
        for world in test_worlds:
            # Infer all facts with axioms
            if self.check_conflict(world, fact):
                new_worlds.append(world)
        return new_worlds

    def check_conflict(self, world, fact):
        # If the fact is Ax_r but it is false in the world assignment, conflict
        if fact[0] == 'A':
            if not fact in world.assignment:
                return False
        # This if it for now
        else:
            return True

    # Implement function remove conflicting worlds
    def add_fact(self, fact, knowledgable_agents):
        new_worlds = []
        # Add fact
        for world in self.worlds:
            new_world = world.copy()
            new_world.assignment[fact] = True
            new_worlds.append(new_world)
        # Remove conflicting worlds
        new_worlds = self.remove_conflicting_worlds(new_worlds, fact)
        # Which agents know the fact?
        agent_names = []
        for agent in knowledgable_agents:
            agent_names.append(agent.name)
        # Add new world to the worlds list
        for world in new_worlds:
            self.worlds.append(world)
            new_world_number = len(self.worlds)
            for agent in self.agents:
                if agent.name not in agent_names:
                    for relation in agent.relations:
                        if relation[0] == new_world_number and \
                           relation[1] == new_world_number:
                            agent.relations.apppend((new_world_number,new_world_number))
                        elif relation[0] == new_world_number:
                            agent.relations.append((relation[0],new_world_number))
                        elif relation[1] == new_world_number:
                            agent.relations.append((new_world_number,relation[1]))