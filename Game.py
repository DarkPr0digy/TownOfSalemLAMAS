from Agent import *
from Event import *
import random


class Game:
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.living_agents = num_agents
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

    # region Day Routines
    def day_routine(self):
        pass

    def _talk(self):
        pass

    def _vote(self):
        pass

    # endregion

    # region Night Routines
    def night_routine(self):
        visitations = {}
        distract_target = None
        heal_target = None
        observe_target = None
        kill_target = None

        for agent in self.agents:
            visitations[agent.name] = []

        # Loop to decide actions
        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Escort:
                    # Distract someone every night
                    distract_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while distract_target.role == Role.Esc:
                        distract_target = self.agents[random.randint(0, self.num_agents - 1)]
                    agent.distract(distract_target)
                    visitations[distract_target.name].append(agent)

                elif agent.role == Role.Lookout:
                    # Observe a player each night
                    observe_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while observe_target.role == Role.LO:
                        observe_target = self.agents[random.randint(0, self.num_agents - 1)]

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    try:
                        while heal_target.used_self_heal:
                            heal_target = self.agents[random.randint(0, self.num_agents - 1)]
                    except AttributeError:
                        pass
                    agent.heal(heal_target)
                    visitations[heal_target.name].append(agent)

                elif agent.role == Role.Vet:
                    # Choose to go active or not based on PR of dying
                    if random.random() < (1/self.living_agents - 1):
                        if agent.used_alert >= 1:
                            agent.change_alert()

                elif agent.role == Role.GF:
                    # Kill someone every night - MVP
                    kill_target = self.agents[random.randint(0, self.num_agents - 1)]
                    while kill_target.role == Role.GF:
                        kill_target = self.agents[random.randint(0, self.num_agents - 1)]

                    if distract_target.role != Role.GF:
                        agent.kill(kill_target)
                        visitations[kill_target.name].append(agent)

                # Skip for now
                elif agent.role == Role.May:
                    pass
                elif agent.role == Role.Vigilante:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")

            #Vet and Doc cant be distracted

        # Loop to execute actions
        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Escort:
                    # Distract someone every night
                    pass

                elif agent.role == Role.Lookout:
                    # Observe a player each night
                    agent.observe(observe_target,
                                  len(visitations[observe_target.name]) > 0,
                                  visitations[observe_target.name])

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    pass

                elif agent.role == Role.Vet:
                    # Enact Killings if Alerted
                    agent.night_action(len(visitations[agent.name]) > 0,
                                       visitations[agent.name])

                    if agent.alert:
                        agent.alert = False

                elif agent.role == Role.GF:
                    # Kill someone every night - MVP
                    pass

                # Skip for now
                elif agent.role == Role.May:
                    pass
                elif agent.role == Role.Vigilante:
                    pass
                else:
                    print("[Error] Something has gone very wrong.")
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
                if agents.role == Role.Mafia:
                    num_mafia_alive += 1
                else:
                    num_agents_alive += 1

        return num_agents_alive == 0 or num_mafia_alive == 0

    def _update_knowledge(self):
        pass


if __name__ == "__main__":
    game = Game(5)
