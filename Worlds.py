from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

import copy
import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

class Worlds:
    def __init__(self, agents, roles, ax):
        self.agents = agents
        self.knowledge_dict = {}
        self.axioms = ax
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
                c_dict = copy.deepcopy(knowledge_dict)
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
                # Reflexivity relation to itself
                relations.append((c_world.name, c_world.name))
                for world in connected_worlds:
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
                del agent.relations[del_rela - counter]
                counter += 1

    def public_announcement(self, fact):
        # In a public announcement, everyone knows that everyone knows that 'fact' is true, and everyone knows
        # that everyone knows that worlds where 'fact' is false is not a feasible world, so remove all worlds
        # where 'fact' is false and remove all relations to the removed worlds
        removed_worlds = []
        for agent in self.agents:
            agent.add_fact(fact)
        # If one of the facts is about a role of a different player:
        # Everyone knows that everyone knows that the role was revealed so
        # Remove worlds where that fact is not in the world assignment
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            removed_worlds = self.remove_worlds(fact)
            self.remove_relations_removed_worlds(removed_worlds, self.agents)

    '''
    --- WIP ---
    def check_worlds_relations(self):
        for agent in self.agents:
            for fact in agent.knowledge:
                # Check if fact is fact about the role of player Ax
                if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
                    # Remove relations that are not possible for agents anymore
    '''

    def remove_worlds(self, fact):
        removed_worlds = []
        for world in self.worlds:
            if fact not in world.assignment:
                removed_worlds.append(world)
        for removed_world in removed_worlds:
            self.worlds.remove(removed_world)
        enablePrint()
        if len(self.worlds) == 0:
            quit()
        blockPrint()
        return removed_worlds

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


    def remove_conflicting_worlds(self, test_worlds, fact, copied_worlds):
        new_worlds = []
        c_worlds = []
        counter = 0
        for world in test_worlds:
            if self.check_conflict(world, fact):
                c_worlds.append(copied_worlds[counter])
                new_worlds.append(world)
            counter += 1
        return new_worlds, c_worlds

    def check_fact_exist(self, fact):
        check = 0
        for world in self.worlds:
            if fact in world.assignment:
                check = 1
        if check == 1:
            return True
        else:
            return False

    # Add more cases if the function will be used
    def check_conflict(self, world, fact):
        # If the fact is Ax_r but it is false in the world assignment, conflict
        if fact[0] == 'A' and len(fact) == 6:
            if not fact in world.assignment:
                return False
        # If the fact is AxVAy_Nn but x is veteran -> conflict
        if fact[2] == 'V' and len(fact) == 8:
            if fact[:2] + '_Vet' in world.assignment:
                return False
        # This if it for now
        return True

    # Likely won't be used (legacy)
    def public_announcement_legacy(self, fact):
        # In a public announcement, everyone knows that everyone knows that 'fact' is true, and everyone knows
        # that everyone knows that worlds where 'fact' is false is not a feasible world, so remove all worlds
        # where 'fact' is false and remove all relations to the removed worlds
        removed_worlds = self.remove_worlds(self.worlds, fact)
        self.remove_relations_removed_worlds(removed_worlds, self.agents)

    # Won't be used (legacy)
    def add_fact_legacy(self, fact, knowledgeable_agents):
        new_worlds = []
        # Add fact
        copied_worlds = []
        for world in self.worlds:
            copied_worlds.append(world.name)
            new_world = copy.deepcopy(world)
            new_world.assignment[fact] = True
            new_worlds.append(new_world)
        # Remove conflicting worlds
        new_worlds, copied_worlds = self.remove_conflicting_worlds(new_worlds, fact, copied_worlds)
        # Which agents know the fact?
        agent_names = []
        for agent in knowledgeable_agents:
            agent_names.append(agent.name)
        counter = 0
        # Add new world to the worlds list
        for world in new_worlds:
            world.name = new_world_number = len(self.worlds)
            ogw = int(copied_worlds[counter])
            counter += 1
            self.worlds.append(world)
            for agent in self.agents:
                if agent.name not in agent_names:
                    copied_relations = copy.deepcopy(agent.relations)
                    for relation in agent.relations:
                        if int(relation[0]) == ogw and int(relation[1]) == ogw:
                            copied_relations.append((new_world_number, new_world_number))
                        elif int(relation[0]) == ogw:
                            copied_relations.append((relation[0], new_world_number))
                        elif int(relation[1]) == ogw:
                            copied_relations.append((new_world_number, relation[1]))
                    agent.relations = copied_relations
