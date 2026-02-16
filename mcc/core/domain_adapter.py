from abc import ABC, abstractmethod

class DomainAdapter(ABC):

    @abstractmethod
    def domain_name(self):
        pass

    @abstractmethod
    def required_parameters(self):
        pass

    @abstractmethod
    def required_assumptions(self):
        pass

    @abstractmethod
    def simulate(self, candidate):
        pass

    @abstractmethod
    def constraints(self):
        pass

    @abstractmethod
    def outputs_of_interest(self):
        pass

    def expected_units(self):
        return {}

    # NEW: optional projection step for design mode
    def project_unknowns(self, params):
        return params
