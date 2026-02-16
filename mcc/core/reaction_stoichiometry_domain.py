from .domain_adapter import DomainAdapter
from .reaction_stoichiometry_simulator import ReactionStoichiometrySimulator
from .stoichiometry_constraints import StoichiometryConstraints

class ReactionStoichiometryDomain(DomainAdapter):
    def __init__(self):
        self.sim = ReactionStoichiometrySimulator()

    def domain_name(self):
        return 'reaction_stoichiometry'

    def required_parameters(self):
        return ['FA0', 'xi1', 'xi2']

    def required_assumptions(self):
        return ['steady_state', 'isothermal']

    def expected_units(self):
        return {
            'FA0': 'mol/s',
            'xi1': 'mol/s',
            'xi2': 'mol/s'
        }

    def simulate(self, candidate):
        return self.sim.run(candidate)

    def constraints(self):
        return [
            StoichiometryConstraints.extents_feasible,
            StoichiometryConstraints.non_negative_flows
        ]

    def outputs_of_interest(self):
        return ['conversion', 'selectivity']
