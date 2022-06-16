from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

class Worlds:
    def __init__(self, agents, roles):
        self.agents = agents
        self.knowledge_dict = {}
        self.worlds = []
        self.worlds = self.create_worlds(self.worlds, self.knowledge_dict,
                                         self.agents, roles)

    def create_worlds(self, worlds, knowledge_dict, agents, roles):
        for x in range(len(agents)):
            agent = agents.pop(0)
            role = roles.pop(x)
            knowledge_dict[agent.name + "_" + str(role)] = True
            if bool(agents):
                worlds = self.create_worlds(worlds, knowledge_dict, agents, roles)
            else:
                # Copy the dictionary so it does not get changed:
                c_dict = knowledge_dict.copy()
                worlds.append(World(str(len(worlds) + 1), c_dict))
            del knowledge_dict[agent.name + "_" + str(role)]
            agents.insert(0, agent)
            roles.insert(x, role)
        self.worlds = worlds
        return worlds

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

    def remove_relations(self, removed_worlds, agents):
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
                del relations[del_rela-counter]
                counter += 1




