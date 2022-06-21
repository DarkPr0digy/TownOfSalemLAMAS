from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *


class Axioms:
    def __init__(self):
        self.axioms = []
        self.facts = []

    def check_axioms(self):
        facts = []
        remove = False
        if not self.axiom_1() is None:
            facts.append(axiom_1())
        axiom_2
        axiom_3
        if conflict:
            remove = True
        return remove

    def axiom_1(self, fact, world, agent, ks):
        # Axiom 1: Kx Ay_r -> -Az_r
        inferred_facts = []
        # Check if fact is correct for axiom 1.
        # It should be of the type 'Ay_rol'
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            # The fact is correct for axiom 1, so extract the role, and agent
            role = fact[3:]
            agent_name = fact[:3]
        else:
            return inferred_facts
        formula = Box(Atom(fact))
        if formula.semantic(ks, world.name):
            counter = 1
            while not agent_name == counter and not agent.name == counter and counter < 5:
                inferred_facts.append("notA"+ str(counter) + "_" + role) # notAy_r
        return inferred_facts

    def axiom_2(self, facts, world, agent, ks):
        # Not necessary, I think
        inferred_facts = []
        return inferred_facts

    def axiom_3(self, facts, world, agent, ks):
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
                            formula = Box(And(Atom(facts[0]), And(Atom(facts[1]), Atom(facts[2]))))
                            if not formula.semantic(ks, world.name):
                                inferred_facts.append("A" + str(x) + "_Vet")
        return inferred_facts

    def axiom_4(self, facts, world, agent, ks):
        # Axiom 4: vVx_Nn ^ not wVx_Nn ^ xD_Nn_GF -> Av_GFR
        inferred_facts = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if facts[0][0] == 'A' and facts[0][3] == '_' and len(facts[0]) == 6 and facts[3:] == 'LOO':
                # Check if second fact has the right format
                if facts[1][1] == 'V' and facts[1][3] == '_' and len(facts[1]) == 6:
                    # Check if third fact has the right format
                    if facts[2][1] == 'D' and facts[2][3] == '_' and facts[2][6:] == 'GF':
                        # Extract the relevant numbers
                        # Check if the same agent is visited
                        if not facts[2][0] == facts[1][3]:
                            return inferred_facts
                        x = facts[1][3]
                        # Check if a different agent visits
                        if not x == facts[1][0]:
                            return inferred_facts
                        v = facts[1][0]
                        # Check if x died the same night v visited
                        if not facts[2][5] == facts[1][6]:
                            return inferred_facts
                        n = facts[2][5]
                        # Check if no one else (w) visited x the same night v visited, where w != x != v
                        counter = 1
                        while counter < 5:
                            if not counter == x and not counter == v:
                                x = 0

    def get_fact_role(self, agent, role=None):
        if role is None:
            return agent.name + "_" + str(agent.role.name)
        else:
            return agent.name + "_" + str(role)

    def get_facts(self, agent):
        # TODO: Not sure this is what he meant
        return agent.facts
