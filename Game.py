from Agent import *
from Event import *
from Worlds import *
from Axiom import Axiom
import random
import itertools
import sys, os
from matplotlib import pyplot as plt
import numpy as np

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


# TODO:
class Game:
    # region Constructor Method
    def __init__(self):
        self.num_days = 0
        self.is_over = False
        self.winner = None
        self.roles = ["Vet", "Doc", "GFR", "May", "LOO"]

        # Create the agents
        self.agents = []
        self.agents.append(Veteran("A1"))
        self.agents.append(Doctor("A2"))
        self.agents.append(Godfather("A3"))
        self.agents.append(Mayor("A4"))
        self.agents.append(Lookout("A5"))

        self.num_agents = len(self.agents)
        self.num_living_agents = self.num_agents

        self.living_agents = ["A1", "A2", "A3", "A4", "A5"]
        self.living_roles = copy.deepcopy(self.roles)

        self.axioms = Axiom(self.roles)

        # Create the worlds
        self.worlds = Worlds(self.agents, self.roles, self.axioms)

    # endregion

    # region Game Routine
    def run_game(self):
        """
        One method that allows the game to be run till it reaches its completion
        :return: Whether town wins or not
        """
        day_counter = 1
        amount_of_worlds = []
        days = []
        for x in range(15):
            days.append(0)
        knowledge_agents = [[],[],[],[],[]]

        # Create the accessibility Relations for Each Agent
        for agent in self.agents:
            self.worlds.create_starting_relations(self.roles, agent)

        # Create the Kripke Structure for Each World
        self.worlds.create_kripke_structures()

        # Create an instance of the axiom class
        axioms = Axiom(self.roles)

        # Game Loop
        game_over, town_wins = self._check_win()
        while not game_over:
            # TODO: This is a test zone - remove later
            ####################################################################
            #self.worlds.public_announcement("A3_GFR")
            #self.agents[2].add_fact("A4_May")
            #self._infer_knowledge(axioms)
            ####################################################################

            print("==================Night %s==================" % str(day_counter))
            for agent in self.agents:
                print(agent.name + ": " + str(agent.role) + " `is alive` is" + str(agent.is_alive))

            # Night Routine
            game_over, town_wins = self.night_routine(day_counter)
            if game_over:
                break

            print("==================Day %s==================" % str(day_counter))

            # Dead agents reveal information
            for agent in self.agents:
                # Look only at dead agents
                if not agent.is_alive and not agent.will_read:
                    # Reveal their role
                    self.worlds.public_announcement(axioms.get_fact_role(agent))

                    # Reveal their last will
                    for fact in agent.knowledge:
                        self.worlds.public_announcement(fact)

                    # Show last will on UI
                    print("\n", agent.get_will(), "\n")

                    agent.will_read = True

            # Update Agent knowledge
            for agent in self.agents:
                print(agent.name + ": " + str(agent.role) + " `is alive` is" + str(agent.is_alive))

            self._infer_knowledge(axioms)

            amount_of_worlds.append(len(self.worlds.worlds))
            days[day_counter-1] += 1
            counter = 0
            for agent in self.agents:
                knowledge_agents[counter].append(len(agent.knowledge)+len(agent.neg_knowledge))
                counter += 1

            # Day Routine
            game_over, town_wins = self.day_routine(day_counter)
            if game_over:
                break

            # TODO: Failsafe GFR - Esc
            ####################################################################
            gfr_esc_only = False
            tmp = 0
            for agent in self.agents:
                if agent.is_alive and agent.role.name == "GFR":
                    tmp += 1
                elif agent.is_alive and agent.role.name == "Esc":
                    tmp += 1

            if tmp == len(self.living_agents):
                gfr_esc_only = True
                game_over = True
                town_wins = False
            ####################################################################
            day_counter += 1

        print("\n=======================Game Over=======================\n")
        if town_wins:
            print("[INFO] Town Wins The Game")
        else:
            print("[INFO] Mafia Wins The Game")

        print("[INFO] Game ends with %d worlds left" % len(self.worlds.worlds))
        for world in self.worlds.worlds:
            print(world.assignment)

        return town_wins, amount_of_worlds, knowledge_agents, days
    # endregion

    # region Day Routines
    def day_routine(self, day):
        """
        The method that controls all events that occur in the day-time cycle of the game
        :return:
        """
        self._talk()
        self._vote(day)

        # Check if Game over
        game_over, town_wins = self._check_win()
        return game_over, town_wins

    def _talk(self):
        """
        The method that allows the agents to talk and share information based on their individual knowledge
        :return:
        """
        print("[INFO] Talking\n=======================================")
        axioms = Axiom(self.roles)
        for agent in self.agents:
            if agent.is_alive:
                #print("Agent ", agent.name)
                true_knowledge_about_my_role = agent.determine_other_agents_knowledge_about_me(self.agents,
                                                                                               game.worlds.worlds)
                my_knowledge_about_others = agent.determine_my_knowledge(game.worlds.worlds, self.living_agents,
                                                                         self.living_roles)
                possible_mafia = agent.determine_who_could_be_mafia(game.worlds.worlds, self.living_agents, self.living_roles,
                                                                    self.agents)
                # print("True knowledge about me", true_knowledge_about_my_role)
                # print("My knowledge about others", my_knowledge_about_others)
                # print("My knowledge possible MAFIA", possible_mafia)


                # If you know other agents know your role make public announcements
                for key in true_knowledge_about_my_role.keys():
                    value = true_knowledge_about_my_role[key]
                    if value is True:
                        # print("[INFO] Enough information about me to share information")
                        # Share Knowledge
                        for fact in agent.knowledge:
                            self.worlds.public_announcement(fact)
                        break
                    else:
                        pass
                        # print("[INFO] Not enough information about me to share information")

        # Update Agents Knowledge
        self._infer_knowledge(axioms)

        # See if Mayor Wants to reveal Self before Vote
        for agent in self.agents:
            if agent.role.name == "May" and agent.is_alive:
                if not agent.is_revealed:
                    agent.determine_reveal_self(self.worlds.worlds, self.living_agents, self.living_roles)

                # Make public announcement if mayor has revealed self
                if agent.is_revealed and not agent.has_announced:
                    agent.reveal_self()
                    fact = agent.name + "_" + agent.role.name
                    self.worlds.public_announcement(fact)
                    self._infer_knowledge(axioms)

    def _vote(self, day):
        """
        The method that allows the agents to vote based on their individual knowledge
        :return:
        """
        print("[INFO] Voting\n=======================================")
        votes = {}
        for agent in self.agents:
            if agent.is_alive:
                print("Agent ", agent.name)
                target_name = agent.determine_who_to_vote_for(self.worlds.worlds, self.living_agents, self.living_roles)

                # Convert Target to Actual Agent
                target = None
                if target_name is not None:
                    for search_agent in self.agents:
                        if search_agent.name == target_name:
                            target = search_agent

                    # Vote For Target
                    target, num_votes = agent.vote(target, day)

                # Get all targets and number of votes
                if target is None:
                    print("[INFO] %s is abstaining" % agent.name)
                else:
                    print("[INFO] %s is voting for %s" % (agent.name, target.name))
                    if target in votes.keys():
                        votes[target] += num_votes
                    else:
                        votes[target] = num_votes

        # Determine Final target
        final_target = None
        max_votes = 0
        for key in votes.keys():
            if votes[key] > max_votes:
                final_target = key
                max_votes = votes[key]

        # TODO: Determine if vote is majority (or other voting rule)
        demoratic = 0
        for _ in self.living_agents:
            demoratic += 1

        if not final_target is None and max_votes >= demoratic + 1 / 2:
            print("[INFO] %s will be voted out democratically" % final_target.name)
            final_target.death()

            # Update living agents and living roles arrays
            self._update_living_agents()

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

        death_prevented = False

        for agent in self.agents:
            visitations[agent.name] = []

        # Loop to decide actions and targets
        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Esc:
                    # Distract someone every night
                    distract_target = agent.determine_who_to_use_ability_on(self.worlds.worlds, self.living_agents, self.living_roles,
                                                          self.agents)
                    agent.distract(distract_target, day)
                    visitations[distract_target.name].append(agent)

                elif agent.role == Role.LOO:
                    # Observe a player each night
                    observe_target = agent.determine_who_to_use_ability_on(self.worlds.worlds, self.living_agents, self.living_roles, self.agents)

                    # print("Observe Target: ", observe_target)

                    visitations[observe_target.name].append(agent)

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    heal_target = agent.determine_who_to_use_ability_on(self.worlds.worlds, self.living_agents, self.living_roles, self.agents)

                    # print("Heal Target: ", heal_target)

                    agent.heal(heal_target, day)
                    heal_target.is_being_healed = True
                    visitations[heal_target.name].append(agent)

                elif agent.role == Role.Vet:
                    # Choose to go active or not based on PR of dying
                    agent.decide_go_active(self.living_agents)

                elif agent.role == Role.GFR:
                    # Kill someone every night - MVP
                    kill_target = agent.determine_who_to_use_ability_on(self.worlds.worlds, self.living_agents, self.living_roles, self.agents)

                    # print("Kill Target: ", kill_target)

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

                elif agent.role == Role.LOO:
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

                    # Check if the doctor healed the should-be-dead-person
                    if len(visitations[agent.name]) > 0 and agent.alert:
                        for vis_agent in visitations[agent.name]:
                            if vis_agent.is_being_healed:
                                death_prevented = True

                    if agent.alert:
                        agent.alert = False

                elif agent.role == Role.GFR:
                    # Kill someone every night - MVP
                    if distract_target is None:
                        agent.kill(kill_target, day)
                        visitations[kill_target.name].append(agent)
                        # Check if the doctor healed the should-be-dead-person
                        if kill_target.is_being_healed:
                            death_prevented = True
                    else:
                        if distract_target.role != Role.GFR:
                            agent.kill(kill_target, day)
                            visitations[kill_target.name].append(agent)
                            # Check if the doctor healed the should-be-dead-person
                            if kill_target.is_being_healed:
                                death_prevented = True

                # Skip for now
                elif agent.role == Role.May:
                    pass

                elif agent.role == Role.Vig:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")

        # Update living agents and living roles arrays
        self._update_living_agents()

        if death_prevented:
            for agent in self.agents:
                if agent.role == Role.Doc:
                    fact = agent.name + 'H' + heal_target.name + '_N' + str(day)
                    agent.add_fact(fact)

        # Check if Game over
        game_over, town_wins = self._check_win()
        return game_over, town_wins

    # endregion

    # region Utility Methods
    def _check_win(self):
        """
        Checks if the game is over.
        :return: True if the game is over, False otherwise.
        """
        num_agents_alive = 0
        num_mafia_alive = 0

        if len(self.worlds.worlds) == 0:
            enablePrint()
            print("-----------------------ERROR-----------------------")
            print("ERROR: There were 0 worlds left after the game finished.\n"
                  "There should be at least 1. Quitting")
            print("-----------------------ERROR-----------------------")
            blockPrint()
            quit()

        for agents in self.agents:
            if agents.is_alive:
                if agents.is_mafia:
                    num_mafia_alive += 1
                else:
                    num_agents_alive += 1

        over = num_agents_alive == 0 or num_mafia_alive == 0
        town_wins = num_mafia_alive == 0

        return over, town_wins

    def _update_living_agents(self):
        """
        Method used to update living agents and living roles
        :return:
        """
        self.num_living_agents = 0
        for agent in self.agents:
            agent.is_being_healed = False
            if agent.is_alive:
                self.num_living_agents += 1

            # Update Living Agents and Roles
            if agent.is_alive is False:
                try:
                    self.living_agents.remove(agent.name)
                except ValueError:
                    pass

                try:
                    self.living_roles.remove(agent.role.name)
                except ValueError:
                    pass

    def _infer_knowledge(self, axioms):
        # Update Agents information after talking
        for agent in self.agents:
            if agent.is_alive:
                agent.infer_facts(axioms)
                agent.update_relations(self.worlds.worlds, axioms)
        self.worlds.remove_redundant_worlds()

    # Won't be used (legacy)
    def _update_knowledge(self):
        for agent in self.agents:
            print(agent.name)
            knowledgeable_agents = []
            for fact in agent.knowledge:
                if not self.worlds.check_fact_exist(fact):
                    print(fact)
                    knowledgeable_agents.append(agent)
                    for kn_agent in self.agents:
                        if kn_agent.name == fact[:2] and \
                                not kn_agent.name == agent.name:
                            knowledgeable_agents.append(kn_agent)
                    self.worlds.add_fact_legacy(fact, knowledgeable_agents)
    # endregion

    # begin region result functions
    def process_data(self, aow_avg, ak_avg, aow, ak):
        for x in range(len(aow)-1):
            if aow[x+1] > aow[x]:
                print("ERROR: Amount of worlds increased!?")
                print(aow)
                quit()
            for y in range(5):
                if ak[y][x + 1] < ak[y][x]:
                    print("ERROR: Amount of knowledge decreased!?")
                    print(ak)
                    quit()
        if len(aow) > 30:
            loop = 30
        else:
            loop = len(aow)
        for x in range(loop):
            aow_avg[x] += aow[x]
            for y in range(5):
                ak_avg[y][x] += ak[y][x]


    def plot_worlds(self, array):
        array = np.array(array)
        plt.plot(array)
        plt.ylabel('Amount of worlds')
        plt.xlabel('Day')
        plt.title('The average amount of worlds that were considered possible by some agent per day')
        plt.show()

    def plot_agent_knowledge(self, array):
        x = 0
        while not array[0][x] == 0:
            x += 1
        counter = 0
        array = np.array(array)
        roles = ['Veteran','Doctor','Godfather','Mayor','Lookout']
        for ar in array:
            plt.plot(ar[:x], label=roles[counter])
            counter += 1
        plt.ylabel('Knowledge (atoms)')
        plt.xlabel('Day')
        plt.title('The average amount of knowledge that each agent had per day')
        plt.legend(loc="upper left")
        plt.show()
    # endregion

if __name__ == "__main__":
    town_wins = 0
    mafia_wins = 0

    days_avg = []
    amount_of_worlds_avg = []
    agent_knowledge_avg = [[], [], [], [], []]
    for x in range(15):
        days_avg.append(0)
        amount_of_worlds_avg.append(0)
        for y in range(5):
            agent_knowledge_avg[y].append(0)


    num_of_games = 1000
    for i in range(num_of_games):
        if i % 10 == 0:
            print("Playing game %d/%d. Town won %d, Mafia won %d" %(i, num_of_games, town_wins, mafia_wins))
        blockPrint()
        game = Game()
        tw, amount_of_worlds, agent_knowledge, days = game.run_game()
        enablePrint()
        game.process_data(amount_of_worlds_avg, agent_knowledge_avg, amount_of_worlds, agent_knowledge)
        for x in range(15):
            days_avg[x] += days[x]
        if tw:
            town_wins += 1
        else:
            mafia_wins += 1

    print(days_avg)
    print(amount_of_worlds_avg)
    print(agent_knowledge_avg)

    for x in range(len(amount_of_worlds_avg)):
        if not amount_of_worlds_avg[x] == 0:
            amount_of_worlds_avg[x] = amount_of_worlds_avg[x] / days_avg[x]
            for y in range(5):
                agent_knowledge_avg[y][x] = agent_knowledge_avg[y][x] / days_avg[x]

    Game().plot_worlds(amount_of_worlds_avg)
    Game().plot_agent_knowledge(agent_knowledge_avg)

    print("Town Wins: ", town_wins)
    print("Mafia Wins: ", mafia_wins)
