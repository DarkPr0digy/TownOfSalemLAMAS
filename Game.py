# region Importing
from copy import deepcopy

from Agent import *
from Agent import Role
from Event import *
from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
import random

# endregion

# TODO: Add a ReadM with run instructions

ROLES = [Role.Vet, Role.Doc, Role.Esc, Role.GF, Role.LO]


class Game:
    def __init__(self):
        self.num_days = 0
        self.is_over = False
        self.winner = None

        # Create the agents
        self.agents = []
        self.agents.append(Veteran("A1"))
        self.agents.append(Doctor("A2"))
        self.agents.append(Escort("A3"))
        self.agents.append(Godfather("A4"))
        self.agents.append(Lookout("A5"))

        # Set the number of agents
        self.num_agents = len(self.agents)
        self.living_agents = self.num_agents

        # TODO: Personal Knowledge of Each Agent??

        # Shared Knowledge of Agents
        self.shared_worlds = []
        self.shared_worlds = self._create_worlds([], deepcopy(self.agents), deepcopy(ROLES), {})

        self.relations_dict = {}
        self._create_starting_relations(self.relations_dict, self.shared_worlds, ROLES)

    # region Day Routines
    def day_routine(self, day):
        """
        Day routine for the game.
        :param day: The day of the game.
        :return:
        """
        pass

    def _talk(self):
        """
        Method that allows the agents to talk during the day, whereby knowledge is shared.
        :return:
        """
        pass

    def _vote(self):
        """
        Method that allows the agents to vote during the day. Only vote if they are confident
        :return: Agent that has been voted out (?)
        """
        pass

    # endregion

    # region Night Routines
    def night_routine(self, day):
        """
        Night routine for the game.
        :param day: The day of the game.
        """
        # Reset variables
        visitations = {}
        distract_target = None
        heal_target = None
        observe_target = None
        kill_target = None

        for agent in self.agents:
            visitations[agent.name] = []

        # Loop to decide actions and targets
        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Esc:
                    # Distract someone every night
                    distract_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while distract_target.role == Role.Esc or distract_target.is_alive is False:
                        distract_target = self.agents[random.randint(0, self.num_agents - 1)]
                    agent.distract(distract_target, day)
                    visitations[distract_target.name].append(agent)

                elif agent.role == Role.LO:
                    # Observe a player each night
                    observe_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while observe_target.role == Role.LO or observe_target.is_alive is False:
                        observe_target = self.agents[random.randint(0, self.num_agents - 1)]
                    visitations[observe_target.name].append(agent)

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    try:
                        while heal_target.used_self_heal or heal_target.is_alive is False:
                            heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    except AttributeError:
                        pass
                    agent.heal(heal_target, day)
                    heal_target.is_being_healed = True
                    visitations[heal_target.name].append(agent)

                elif agent.role == Role.Vet:
                    # Choose to go active or not based on PR of dying
                    alert_prob = random.random()
                    if alert_prob < 1 / (self.living_agents - 1):
                        if agent.used_alert >= 1:
                            print("[INFO] Vet Is Going Active")
                            agent.change_alert()

                elif agent.role == Role.GF:
                    # Kill someone every night
                    kill_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while kill_target.role == Role.GF or kill_target.is_alive is False:
                        kill_target = self.agents[random.randint(0, self.num_agents - 1)]
                    visitations[kill_target.name].append(agent)

                # Skip for now
                elif agent.role == Role.May:
                    pass
                elif agent.role == Role.Vig:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")

        print("[Night] Visitations: " + str(visitations))
        print("[Night] Distract Target: " + str(distract_target))
        print("[Night] Heal Target: " + str(heal_target))
        print("[Night] Observe Target: " + str(observe_target))
        print("[Night] Kill Target: " + str(kill_target))

        # Loop to execute actions
        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Esc:
                    # Distract someone every night
                    pass

                elif agent.role == Role.LO:
                    # Observe a player each night
                    agent.observe(observe_target,
                                  len(visitations[observe_target.name]) > 0,
                                  visitations[observe_target.name],
                                  day)

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    pass

                elif agent.role == Role.Vet:
                    # Enact Killings if Alerted
                    agent.night_action(len(visitations[agent.name]) > 0,
                                       visitations[agent.name],
                                       day)

                    if agent.alert:
                        agent.alert = False

                elif agent.role == Role.GF:
                    # Kill someone every night - MVP
                    if distract_target is None:
                        agent.kill(kill_target, day)
                    else:
                        if distract_target.role != Role.GF:
                            agent.kill(kill_target, day)


                # Skip for now
                elif agent.role == Role.May:
                    pass
                elif agent.role == Role.Vigilante:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")

        # Count Living Agents
        self.living_agents = 0
        for agent in self.agents:
            agent.is_being_healed = False
            if agent.is_alive:
                self.living_agents += 1

        # TODO: Knowledge Updates
        if observe_target is not None:
            if len(visitations[observe_target.name]) == 2 and not observe_target.is_alive:
                # TODO: Need a better way to find agents
                visitations[observe_target.name].remove(self.agents[4])
                mafia = visitations[observe_target.name][0]
                self.agents[4].knowledge[mafia.name + "_" + str(mafia.role)] = True

    # endregion

    # region Utility Methods
    def _check_win(self):
        """
        Checks if the game is over.
        :return: True if the game is over, False otherwise.
        """
        num_agents_alive = 0
        num_mafia_alive = 0

        for agents in self.agents:
            if agents.is_alive:
                if agents.role == Role.GF:
                    num_mafia_alive += 1
                else:
                    num_agents_alive += 1

        return num_agents_alive == 0 or num_mafia_alive == 0

    def _update_knowledge(self):
        """
        Updates the knowledge of the agents.
        :return:
        """
        pass

    def _create_worlds(self, worlds, agent_list, role_list, dict):
        """
        Recursive Function used to create the Kripke Worlds
        :param agent_list: List of agents
        :param role_list: List of roles
        :param dict: dict to be passed through the recursive function
        :return: List of Kripke Worlds
        """
        for x in range(len(agent_list)):
            c_agent = agent_list.pop(0)
            c_role = role_list.pop(x)
            dict[c_agent.name + str(c_role)] = True
            if bool(agent_list):
                worlds = self._create_worlds(worlds, agent_list, role_list, dict)
            else:
                # Copy the dictionary so it does not get changed:
                c_dict = dict.copy()
                worlds.append(World(str(len(worlds) + 1), c_dict))
            del dict[c_agent.name + str(c_role)]
            agent_list.insert(0, c_agent)
            role_list.insert(x, c_role)
        return worlds

    def _create_starting_relations(self, relations_dict, worlds, roles):
        """
        Creates the starting relations for the Kripke Worlds
        :param relations_dict:
        :param worlds:
        :param roles:
        :return:
        """
        # Function creates only worlds for agents 1 and 2 and not 3,
        # has to do with the names in the dictionary
        # This function can be changed to make it so that you give
        # the name of the agent and it fetches the relations for that particular agent
        for agent in self.agents:
            x = agent.name
            relations_dict[str(x)] = {}
            relations = []
            for role in roles:
                connected_worlds = []
                for world in range(len(worlds)):
                    if str(x) + str(role) in worlds[world].assignment:
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
            relations_dict[str(x)] = relations
    # endregion


if __name__ == "__main__":
    game = Game()
    day_counter = 1
    while not game._check_win():
        print("==================\nDay Time\n==================")
        for agents in game.agents:
            print(agents.name + ": " + str(agents.role) + " `is alive` is" + str(agents.is_alive))

        game.night_routine(day=day_counter)
        print("==================\nNight Time\n==================")

        for agents in game.agents:
            print(agents.name + ": " + str(agents.role) + " `is alive` is" + str(agents.is_alive))

        day_counter += 1

    print("\n=======================Game Over=======================\n")
    for agents in game.agents:
        if not agents.is_alive:
            will, _, _ = agents.get_will()
            print(will)
