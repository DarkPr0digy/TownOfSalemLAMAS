from Agent import *
from Event import *
from Worlds import *
import random


class Game:
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.living_agents = num_agents
        self.num_days = 0
        self.is_over = False
        self.winner = None
        self.roles = ["Vet", "Doc", "LOO", "GFR"]

        # Create the agents
        self.agents = []
        self.agents.append(Veteran("A1"))
        self.agents.append(Doctor("A2"))
        # self.agents.append(Escort("A3"))
        self.agents.append(Godfather("A4"))
        self.agents.append(Lookout("A5"))

        # Create the worlds
        self.worlds = Worlds(self.agents, self.roles)

    # region Day Routines
    def day_routine(self):
        pass

    def _talk(self):
        pass

    def _vote(self):
        pass

    # endregion

    # region Night Routines
    def night_routine(self, day):
        # TODO: If vet is active and GF visits, GF should die
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

                elif agent.role == Role.LOO:
                    # Observe a player each night
                    observe_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while observe_target.role == Role.LOO or observe_target.is_alive is False:
                        observe_target = self.agents[random.randint(0, self.num_agents - 1)]

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while heal_target.role == Role.Doc or heal_target.is_alive is False:
                        heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    agent.heal(heal_target, day)
                    heal_target.is_being_healed = True
                    visitations[heal_target.name].append(agent)

                elif agent.role == Role.Vet:
                    # Choose to go active or not based on PR of dying
                    alert_prob = random.random()
                    if alert_prob < 1/(self.living_agents - 1):
                        if agent.used_alert >= 1:
                            print("[INFO] Vet Is Going Active")
                            agent.change_alert()

                elif agent.role == Role.GFR:
                    # Kill someone every night - MVP
                    kill_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while kill_target.role == Role.GFR or kill_target.is_alive is False:
                        kill_target = self.agents[random.randint(0, self.num_agents - 1)]

                # Skip for now
                elif agent.role == Role.May:
                    pass
                elif agent.role == Role.Vig:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")

        print("[Night] Visitations: "+str(visitations))
        print("[Night] Distract Target: "+str(distract_target))
        print("[Night] Heal Target: "+str(heal_target))
        print("[Night] Observe Target: "+str(observe_target))
        print("[Night] Kill Target: "+str(kill_target))

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

                    if agent.alert:
                        agent.alert = False

                elif agent.role == Role.GFR:
                    # Kill someone every night - MVP
                    if distract_target is None:
                        agent.kill(kill_target, day)
                        visitations[kill_target.name].append(agent)
                    else:
                        if distract_target.role != Role.GFR:
                            agent.kill(kill_target, day)
                            visitations[kill_target.name].append(agent)

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

        self._update_knowledge()
    # endregion

    def _check_win(self):
        """
        Checks if the game is over.
        :return: True if the game is over, False otherwise.
        """
        num_agents_alive = 0
        num_mafia_alive = 0

        for agents in self.agents:
            if agents.is_alive:
                if agents.role == Role.GFR:
                    num_mafia_alive += 1
                else:
                    num_agents_alive += 1

        return num_agents_alive == 0 or num_mafia_alive == 0

    def _update_knowledge(self):
        for agent in self.agents:
            knowledgeable_agents = []
            for fact in agent.knowledge:
                if not self.worlds.check_fact_exist(fact):
                    knowledgeable_agents.append(agent)
                    for kn_agent in self.agents:
                        if kn_agent.name == fact[:2] and \
                                not kn_agent.name == agent.name:
                            knowledgeable_agents.append(kn_agent)
                    self.worlds.add_fact(fact, knowledgeable_agents)

if __name__ == "__main__":
    game = Game(4)
    day_counter = 1
    # For each agent, create the accessibility relations
    for agent in game.agents:
        game.worlds.create_starting_relations(game.roles, agent)
    game.worlds.create_kripke_structures()
    while not game._check_win():
        print("==================\nDay Time\n==================")
        for agents in game.agents:
            print(agents.name + ": " + str(agents.role) + " `is alive` is" + str(agents.is_alive))

        game.night_routine(day=day_counter)

        print("==================\nNight Time\n==================")

        for agents in game.agents:
            print(agents.name + ": " + str(agents.role) + " `is alive` is" + str(agents.is_alive))

        day_counter += 1

        print("The amount of worlds before dead: %d" % len(game.worlds.worlds))
        for agent in game.agents:
            print(agent.relations)
            if not agent.is_alive:
                # Reveal the role of the dead agent
                game.worlds.public_announcent(game.worlds.axioms.get_fact_role(agent))
                # Reveal last will
                for fact in agent.knowledge:
                    game.worlds.public_announcent(fact)

        if len(game.worlds.worlds) == 0:
            print("[ERROR]: Something went wrong, quitting")
            quit()

    print("\n=======================Game Over=======================\n")
    for agents in game.agents:
        for fact in agents.knowledge:
            game.worlds.public_announcent(fact)
        if not agents.is_alive:
            will, _, _ = agents.get_will()
            print(will)

    print("Game ends with %d worlds left" %len(game.worlds.worlds))
    for world in game.worlds.worlds:
        print(world.assignment)
