from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

class Axioms:
    def __init__(self):
        self.axioms = []
        self.facts = []


    def check_axioms(self):
        facts = []
        remove = False
        if not axiom_1() is None:
            facts.append(axiom_1())
        axiom_2
        axiom_3
        if conflict:
            remove = True
        return remove


    def axiom_1(self, fact1, worlds, agents):
        formula = Box(Atom(fact1))
        formula.semantic(ks, '1')
        if formula.semantic(ks, '1') == True:
            inferred_fact = 0
            return inferred_fact

    def get_fact_role(self, agent, role=None):
        if role is None:
            return agent.name + "_" + str(agent.role.name)
        else:
            return agent.name + "_" + str(role)
