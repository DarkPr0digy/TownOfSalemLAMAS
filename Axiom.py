from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *


class Axiom:
    def __init__(self):
        self.axioms = []
        self.facts = []

    # Axioms 1 and 2 are axioms to be applied generally
    def axiom_1(self, fact, agent):
        # Axiom 1: Kx Ay_r -> -Az_r
        inferred_facts = []
        # Check if fact is correct for axiom 1.
        # It should be of the type 'Ay_rol'
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            # The fact is correct for axiom 1, so extract the role, and agent
            role = fact[3:]
            agent_name = fact[:2]
        else:
            return inferred_facts
        for counter in range(1, 6):
            if not agent_name == 'A' + str(counter):
                inferred_facts.append("notA" + str(counter) + "_" + role)  # notAy_r
        return inferred_facts

    # If I know all but one agent isn't some role, the last agent has that role
    def axiom_2A(self, facts):
        inferred_facts = []
        agent_names = []
        # Extract role
        role = facts[0][6:]
        for fact in facts:
            if not role == fact[6:]:
                return inferred_facts
            else:
                agent_names.append(fact[4])
        for x in range(1,6):
            if str(x) not in agent_names:
                inferred_facts.append('A' + str(x) + '_' + role)
                return inferred_facts

        print("ERROR: Something went wrong with axiom 2A, quitting")
        quit()
        return inferred_facts

    # If I know all that an agent does not have role a,b,c and d, we can infer it has role e
    def axiom_2B(self, facts):
        inferred_facts = []
        agent_names = []
        # Extract role
        role = facts[0][6:]
        for fact in facts:
            if not role == fact[6:]:
                return inferred_facts
            else:
                agent_names.append(fact[4])
        for x in range(1,6):
            if str(x) not in agent_names:
                inferred_facts.append('A' + str(x) + '_' + role)
                return inferred_facts

        print("ERROR: Something went wrong with axiom 2B, quitting")
        quit()
        return inferred_facts

    # Axioms 3 and 4 are only for the lookout
    def axiom_3(self, facts):
        # Au_LOO ^ vVx_Nn ^ wVx_Nn -> Ax_Vet
        inferred_facts = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if facts[0][0] == 'A' and facts[0][3] == '_' and len(facts[0]) == 6 and facts[3:] == 'LOO':
                # Check if second fact has the right format
                if facts[1][1] == 'V' and facts[1][3] == '_' and len(facts[1]) == 6:
                    # Check if third fact has the right format
                    if facts[2][1] == 'V' and facts[2][3] == '_' and len(facts[2]) == 6:
                        # Extract the relevant numbers
                        u = facts[0][1]
                        v = facts[1][0]
                        w = facts[2][1]
                        x = facts[1][2]
                        if not u == v and not u == w and not v == w and x == facts[2][2]:
                            inferred_facts.append("A" + str(x) + "_Vet") # A1_Vet
        return inferred_facts

    # Works for more roles as well (probably)
    def axiom_4(self, facts, knowledge):
        # Axiom 4: Au_LOO ^ vVx_Nn ^ xD_Nn_GF -> Av_GFR
        inferred_facts = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'LOO':
                # Check if second fact has the right format
                if self.check_fact_is_visit(facts[1]):
                    # Check if third fact has the right format
                    if facts[2][1] == 'D' and facts[2][3] == '_' and facts[2][6:] == 'GFR':
                        # Extract the relevant numbers
                        # Check if the same agent is visited
                        if not facts[1][2] == facts[2][0]:
                            return inferred_facts
                        x = facts[1][2]
                        # Check if a different agent visits
                        if not x == facts[1][0]:
                            return inferred_facts
                        v = facts[1][0]
                        # Check if x died the same night v visited
                        if not facts[2][4] == facts[1][5]:
                            return inferred_facts
                        n = facts[2][5]
                        # Check if no one else (w) visited x the same night v visited, where w != x != v
                        for fact in knowledge:
                            # wVx_Nn
                            if self.check_fact_is_visit(fact):
                                if fact[5] == n and not fact[0] == v and fact[2] == x:
                                    return inferred_facts
                        # If more mafia agents, this should be mafia instead of GFR
                        # TODO: if roles are added, change this infer
                        inferred_facts.append("A" + str(v) + "_GFR")
        return inferred_facts

    def check_fact_is_role(self, fact):
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            return True
        else:
            return False

    def check_fact_is_visit(self, fact):
        if fact[1] == 'V' and fact[3] == '_' and len(fact) == 6:
            return True
        else:
            return False

    def get_fact_role(self, agent, role=None):
        if role is None:
            return agent.name + "_" + str(agent.role.name)
        else:
            return agent.name + "_" + str(role)

    def get_facts(self, agent):
        # TODO: Not sure this is what he meant
        return agent.facts
