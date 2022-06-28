from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *

class Axiom:
    def __init__(self, roles):
        self.axioms = []
        self.facts = []
        self.roles = roles

    # Axioms 1 and 2 are axioms to be applied generally
    def axiom_1(self, fact, agent):
        # Axiom 1: Kx Ay_r -> -Az_r
        inferred_facts = []
        # Check if fact is correct for axiom 1.
        # It should be of the type 'Ay_rol'
        if self.check_fact_is_role(fact):
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
    def axiom_2B(self, facts, Role):
        inferred_facts = []
        accounted_for_roles = []
        # Extract role
        agent_name = facts[0][4]
        for fact in facts:
            if not agent_name == fact[4]:
                return inferred_facts
            else:
                accounted_for_roles.append(fact[6:])
        for role in Role:
            if role.name not in accounted_for_roles and role.name in self.roles:
                inferred_facts.append('A' + agent_name + '_' + role.name)
                return inferred_facts

        print("ERROR: Something went wrong with axiom 2B, quitting")
        quit()
        return inferred_facts

    # Axioms 3, 4, 5 and 6 are only for the lookout
    def axiom_3(self, facts):
        # Au_LOO ^ AvVAx_Nn ^ AwVAx_Nn -> v and w are not Doc or GF
        inferred_facts = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'LOO':
                # Check if second fact has the right format
                if self.check_fact_is_visit(facts[1]):
                    # Check if third fact has the right format
                    if self.check_fact_is_visit(facts[2]):
                        # Check if they visited the same night
                        if facts[1][7] == facts[2][7]:
                            # Extract the relevant numbers
                            u = facts[0][1]
                            v = facts[1][1]
                            w = facts[2][1]
                            x = facts[1][4]
                            if not u == v and not u == w and not v == w and x == facts[2][4]:
                                for count in range(1,6):
                                    if not str(count) == w and not str(count) == v:
                                        # V and w are doc and gfr, so no one else is
                                        inferred_facts.append("notA" + str(count) + "_Doc")
                                        inferred_facts.append("notA" + str(count) + "_GFR")
                                for count in [v, w]:
                                    inferred_facts.append("notA" + count + "_LOO")
                                    inferred_facts.append("notA" + count + "_Doc")
                                    inferred_facts.append("notA" + count + "_GFR")
        return inferred_facts

    def axiom_4(self, facts):
        # Axiom 4: Au_LOO ^ AxVAy_Nn -> notAx_vet ^ notAx_May
        inferred_facts = []
        if len(facts) == 2:
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'LOO':
                if self.check_fact_is_visit(facts[1]):
                    x = facts[1][1]
                    inferred_facts.append("notA" + x + "_Vet")
                    inferred_facts.append("notA" + x + "_May")
        return inferred_facts

    def axiom_5(self, facts, knowledge):
        # Axiom 5: Au_LOO ^ AvVAx_Nn ^ xD_Nn_GFR -> Av_GFR
        inferred_facts = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'LOO':
                # Check if second fact has the right format
                if self.check_fact_is_visit(facts[1]):
                    # Check if third fact has the right format
                    if self.check_fact_is_dead(facts[2]) and facts[2][6:] == 'GFR':
                        # Extract the relevant numbers
                        # Check if the same agent is visited
                        if not facts[1][4] == facts[2][0]:
                            return inferred_facts
                        x = facts[1][4]
                        # Check if a different agent visits
                        if x == facts[1][1]:
                            return inferred_facts
                        v = facts[1][1]
                        # Check if x died the same night v visited
                        if not facts[2][4] == facts[1][7]:
                            return inferred_facts
                        n = facts[2][4]
                        # Check if no one else (w) visited x the same night v visited, where w != x != v
                        for fact in knowledge:
                            # AwVAx_Nn
                            if self.check_fact_is_visit(fact):
                                if fact[7] == n and not fact[1] == v and fact[4] == x:
                                    return inferred_facts
                        # If more mafia agents, this should be mafia instead of GFR
                        inferred_facts.append("A" + str(v) + "_GFR")
        return inferred_facts

    def axiom_6(self, facts):
        # Axiom 6: Au_LOO ^ AxVAy_Nn ^ zD_Nn_GF -> w in A for w =/= x,y,z,u: Aw_GFR
        inferred_facts = []
        agents = []
        if len(facts) == 3:
            # Check if first fact has the right format
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'LOO':
                if self.check_fact_is_visit(facts[1]):
                    if self.check_fact_is_dead(facts[2]) and facts[2][6:] == 'GFR':
                        if facts[1][7] == facts[2][4]:
                            agents.append(facts[1][4])
                            agents.append(facts[2][0])
                            agents.append(facts[0][1])
                            x = facts[1][1]
                            if x not in agents:
                                agents.append(x)
                                for count in range(1,6):
                                    if str(count) not in agents:
                                        inferred_facts.append("A" + str(count) + "_GFR")
        return inferred_facts

    def axiom_7(self, facts):
        # Axiom 7: Au_Doc ^ AuHAx_Nn ^ yD_Nm_GFR ^ Ay_Vet
        inferred_facts = []
        if len(facts) == 4:
            if self.check_fact_is_role(facts[0]) and facts[0][3:] == 'Doc':
                if self.check_fact_is_heal(facts[1]):
                    if self.check_fact_is_dead(facts[2]) and facts[2][6:] == 'GFR':
                        if self.check_fact_is_role(facts[3]) and facts[3][3:] == 'Vet':
                            u = facts[0][1]
                            x = facts[1][4]
                            y = facts[2][0]
                            n = facts[1][7]
                            m = facts[2][4]
                            if facts[1][1] == u and not u == y and not y == x \
                                    and y == facts[3][1] and int(m) < int(n):
                                inferred_facts.append('notA' + x + '_GFR')
        return inferred_facts



    def check_fact_is_role(self, fact):
        if fact[0] == 'A' and fact[2] == '_' and len(fact) == 6:
            return True
        else:
            return False

    def check_fact_is_visit(self, fact):
        if fact[2] == 'V' and fact[5] == '_' and len(fact) == 8:
            return True
        else:
            return False

    def check_fact_is_heal(self, fact):
        if fact[2] == 'H' and fact[5] == '_' and len(fact) == 8:
            return True
        else:
            return False

    def check_fact_is_dead(self, fact):
        if fact[1] == 'D' and fact[3] == 'N' and len(fact) == 9:
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
