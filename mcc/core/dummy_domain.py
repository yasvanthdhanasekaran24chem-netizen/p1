from .domain_adapter import DomainAdapter
from .simulation_interface import SimulationResult

class DummyDomain(DomainAdapter):
    def domain_name(self):
        return "dummy"

    def required_parameters(self):
        return []

    def required_assumptions(self):
        return []

    def simulate(self, candidate):
        return SimulationResult(outputs={})

    def constraints(self):
        return []

    def outputs_of_interest(self):
        return []
