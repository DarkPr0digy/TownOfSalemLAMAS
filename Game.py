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
        # TODO: IF agent alive - do ability - if dead - do nothing
        # TODO: track all agent decisions to pass necessary info to necessary agents

        for agent in self.agents:
            if agent.is_alive:
                if agent.role == Role.Lookout:
                    # Observe a player each night
                    target = self.agents[random.randint(0, self.num_agents - 1)]
                    while target.role == Role.LO:
                        target = self.agents[random.randint(0, self.num_agents - 1)]
                    # TODO: Fill in these methods with the appropriate information
                    agent.observe(target, False, [])

                elif agent.role == Role.Doc:
                    # Heal a player each night
                    target = self.agents[random.randint(0, self.num_agents - 1)]
                    try:
                        while target.used_self_heal:
                            target = self.agents[random.randint(0, self.num_agents - 1)]
                    except AttributeError:
                        pass
                    agent.heal(target)

                elif agent.role == Role.Vet:
                    # TODO: Change Alert Status at end of night
                    # Choose to go active or not based on PR of dying
                    if random.random() < (1/self.living_agents - 1):
                        if agent.used_alert >= 1:
                            agent.change_alert()
                    # TODO: Implement vet night action
                    agent.night_action(is_visited=False, visitors=[])

                elif agent.role == Role.Escort:
                    # Distract someone every night
                    target = self.agents[random.randint(0, self.num_agents - 1)]
                    while target.role == Role.Esc:
                        target = self.agents[random.randint(0, self.num_agents - 1)]
                    agent.distract(target)

                elif agent.role == Role.GF:
                    # Kill someone every night - MVP
                    target = self.agents[random.randint(0, self.num_agents - 1)]
                    while target.role == Role.GF:
                        target = self.agents[random.randint(0, self.num_agents - 1)]
                    agent.kill(target)

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
