'''
Naming convention for atoms:
Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
Player 1 is Escort: '1E'
Player 1 visited player 3 on night 2: '1v3n2'
((not 1v3n2) and (d3n2)) --> not 1G
'''

from mlsolver.kripke import World, KripkeStructure

# Amount of agents in the game
NO_OF_AGENTS = 5
dict = {}

# Recursive function to create the worlds
def create_worlds(worlds, agents, roles, dict):
    for x in range(len(agents)):
        c_agent = agents.pop(0)
        c_role = roles.pop(x)
        dict[str(c_agent+c_role)] = True
        if bool(agents):
            worlds = create_worlds(worlds, agents, roles, dict)
        else:
            worlds.append(World(str(len(worlds) + 1), dict))
        agents.insert(0, c_agent)
        roles.insert(x, c_role)
    return worlds

# Agents and roles, where roles are abbreviations:
# Escort = 'E', Veteran = 'V', Doctor = 'D', Godfather = 'G', Lookout = 'L'
agents = []
roles = ['D', 'E', 'G', 'L', 'V']

# List of worlds
worlds = []

# Create a list with the name of the agents:
# list will be ['1', '2', '3'] etc for the NO_OF_AGENTS agents
for x in range(NO_OF_AGENTS):
    agents.append(str(x+1))

# Create the worlds
worlds = create_worlds(worlds, agents, roles, dict)

# There will be NO_OF_AGENTS! amount of worlds (e.g. 5 agents = 5! = 120 worlds)
print(len(worlds))


