'''
Naming convention for atoms:
Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
Player 1 is Escort: '1E'
Player 1 visited player 3 on night 2: '1v3n2'
((not 1v3n2) and (d3n2)) --> not 1G
'''
import copy

from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

# Amount of agents in the game
# 6 is the limit
NO_OF_AGENTS = 3
# Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
ROLES = ['D', 'E', 'G', 'L', 'V']


# Recursive function to create the worlds
def create_worlds(worlds, agents, roles, dict):
    for x in range(len(agents)):
        c_agent = agents.pop(0)
        c_role = roles.pop(x)
        dict[str(c_agent + c_role)] = True
        if bool(agents):
            worlds = create_worlds(worlds, agents, roles, dict)
        else:
            # Copy the dictionary so it does not get changed:
            c_dict = dict.copy()
            worlds.append(World(str(len(worlds) + 1), c_dict))
        del dict[str(c_agent + c_role)]
        agents.insert(0, c_agent)
        roles.insert(x, c_role)
    return worlds


# Function creates only worlds for agents 1 and 2 and not 3,
# has to do with the names in the dictionary
def create_starting_relations(relations_dict, worlds, roles, agents):
    # This function can be changed to make it so that you give
    # the name of the agent and it fetches the relations for that particular agent
    for x in range(len(agents)):
        relations_dict[str(agents[x])] = {}
        relations = []
        for role in roles:
            connected_worlds = []
            for world in range(len(worlds)):
                if str(agents[x]) + role in worlds[world].assignment:
                    connected_worlds.append(world)
            # In every connected the agent has the role 'role', so there should be a relation between them
            while bool(connected_worlds):
                c_world = connected_worlds.pop(0)
                for z in connected_worlds:
                    # Assume reflexivity
                    relations.append((str(c_world + 1), str(c_world + 1)))
                    relations.append((str(z + 1), str(z + 1)))
                    # Assume the other one
                    relations.append((str(c_world + 1), str(z + 1)))
                    relations.append((str(z + 1), str(c_world + 1)))
                    # Add something for transitivity
        relations_dict[agents[x]] = relations


def remove_relations(removed_worlds, relations_dict):
    for agent_rels in relations_dict:
        relations = relations_dict[agent_rels]
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


def remove_worlds(worlds, fact):
    removed_worlds = []
    for world in worlds:
        if fact not in world.assignment:
            removed_worlds.append(world)
    for removed_world in removed_worlds:
        worlds.remove(removed_world)
    return worlds, removed_worlds


def public_announcement(fact, worlds, relation_dict):
    # In a public announcement, everyone knows that everyone knows that 'fact' is true, and everyone knows
    # that everyone knows that worlds where 'fact' is false is not a feasible world, so remove all worlds
    # where 'fact' is false and remove all relations to the removed worlds
    worlds, removed_worlds = remove_worlds(worlds, fact)
    remove_relations(removed_worlds, relation_dict)
    return worlds


def add_fact(fact, worlds, relation_dict, observer):  # Observer is an agent
    x = 0
    # agent x observes y visits z (yVz)
        # if x = y, thus x visits z, same procedure, cuz x knows that x visited y
    # for every world where x is lookout, add yVz to those worlds
    # add relation between new and old world for all agents except the x and y


def do_simulation(agents=None):
    if agents is None:
        agents = []
    won = False
    dead_agents = []
    while not won:
        # Night -----------
        # Do abilities + give knowledge from abilities
        for agent in agents:
            agent.ability()
        # Decide which agents died and add them to a list
        dead_agents.append(None)

        # Day -------------
        # Show which agents died
        # Did any faction win?
        while not len(dead_agents) == 0:
            dead_agent = dead_agents.pop()
            name = dead_agent.name
            role = dead_agent.role
            last_will = dead_agent.last_will
            for agent in agents:
                agent.add_knowledge(name + 'dead')
                agent.add_knowledge(name + role)
                agent.add_knowledge(last_will)
        # Give agents knowledge of the role of the dead agent
        # Give agents knowledge of the last will of te dead agent (public announcement)
        # Remove worlds where the dead agent does not have the role that was shown (public announcement)
        # Remove accessibility relations to the removed world
        # Update accessibility relations for each agent
        # Update possible worlds (if a world has no accessibility relations and it is not the true world, remove it,
        # its not relevant)
        # Check if agent knows that all other agents know his role (K role(agent)). If this is the case and the agent is
        # a townie, he can give information and everyone will see it as truth because townies don't lie
        # Each agent votes if they know for sure that agent x is bad. agent x gets lynched if majority votes agent x
        # Won?

        # Night ----------
        # repeat.


def main():
    # Agents and roles
    agents = []
    roles = ROLES[:NO_OF_AGENTS]

    # List of worlds
    worlds = []

    # Create a list with the name of the agents:
    # list will be ['1', '2', '3'] etc for the NO_OF_AGENTS agents
    for x in range(NO_OF_AGENTS):
        agents.append(str(x + 1))

    # Create the worlds
    dict = {}
    worlds = create_worlds(worlds, agents, roles, dict)

    # Create the relations between worlds for every agent
    relations_dict = {}
    create_starting_relations(relations_dict, worlds, roles, agents)

    worlds = public_announcement('1D', worlds, relations_dict)

    # Kripke structure for agent 1
    ks = KripkeStructure(worlds, relations_dict['1'])

    # In world 2, for agent 1, 1D is true in every reachable world, because
    # agent 1 can reach world 1 and world 2 from world 2, thus we have
    # (ks,w2) |= K_1 1D, thus the formula is true
    formula = Implies(Diamond(Atom('2E')), Atom('1D'))  # M_1 2E ^ 1D
    formula = And(Atom('3E'),Atom('4E'))
    print(formula.semantic(ks, '1'))

    print("All the possible worlds with their atomic propositions:")
    for world in worlds:
        print(world)
    quit()
    # There will be NO_OF_AGENTS! amount of worlds (e.g. 5 agents = 5! = 120 worlds)
    print(len(worlds))


if __name__ == '__main__':
    main()
