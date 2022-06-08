'''
Naming convention for atoms:
Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
Player 1 is Escort: '1E'
Player 1 visited player 3 on night 2: '1v3n2'
((not 1v3n2) and (d3n2)) --> not 1G
'''

from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

# Amount of agents in the game
# 6 is the limit
NO_OF_AGENTS = 5
# Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
ROLES = ['D', 'E', 'G', 'L', 'V']


# Recursive function to create the worlds
def create_worlds(worlds, agents, roles, dict):
    for x in range(len(agents)):
        c_agent = agents.pop(0)
        c_role = roles.pop(x)
        dict[str(c_agent+c_role)] = True
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
def create_starting_relations(relations_dict, worlds, roles):
    # This function can be changed to make it so that you give
    # the name of the agent and it fetches the relations for that particular agent
    for x in range(NO_OF_AGENTS):
        relations_dict[str(x)] = {}
        relations = []
        for role in roles:
            connected_worlds = []
            for world in range(len(worlds)):
                if str(x)+role in worlds[world].assignment:
                    connected_worlds.append(world)
            # In every connected the agent has the role 'role', so there should be a relation between them
            while bool(connected_worlds):
                c_world = connected_worlds.pop(0)
                for z in connected_worlds:
                    # Assume reflexivity
                    relations.append((str(c_world + 1), str(c_world + 1)))
                    relations.append((str(z+1), str(z+1)))
                    # Assume the other one
                    relations.append((str(c_world+1), str(z+1)))
                    relations.append((str(z + 1), str(c_world + 1)))
                    # Add something for transitivity
        relations_dict[str(x)] = relations


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
        agents.append(str(x+1))

    # Create the worlds
    dict = {}
    worlds = create_worlds(worlds, agents, roles, dict)

    # Create the relations between worlds for every agent
    relations_dict = {}
    create_starting_relations(relations_dict, worlds, roles)

    # Kripke structure for agent 1
    ks = KripkeStructure(worlds, relations_dict['1'])

    # In world 2, for agent 1, 1D is true in every reachable world, because
    # agent 1 can reach world 1 and world 2 from world 2, thus we have
    # (ks,w2) |= K_1 1D, thus the formula is true
    formula = Implies(Diamond(Atom('2E')),Atom('1D')) # M_1 2E ^ 1D
    print(formula.semantic(ks, '1'))

    print("Accessibility relations for agent 1:")
    print(relations_dict['1'])

    print("All the possible worlds with their atomic propositions:")
    print(worlds[0])
    print(worlds[1])
    print(worlds[2])
    print(worlds[3])
    print(worlds[4])
    print(worlds[5])

    # There will be NO_OF_AGENTS! amount of worlds (e.g. 5 agents = 5! = 120 worlds)
    print(len(worlds))

if __name__ == '__main__':
    main()
