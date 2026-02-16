from .domain_adapter import DomainAdapter
from .component_mass_balance_simulator import ComponentMassBalanceSimulator
from .engineering_constraints import EngineeringConstraints

class ComponentMassBalanceDomain(DomainAdapter):
    def __init__(self):
        self.simulator = ComponentMassBalanceSimulator()

    def domain_name(self) -> str:
        return "component_mass_balance"

    def required_parameters(self) -> list:
        return [
            "inlet_components",
            "outlet_components"
        ]

    def required_assumptions(self) -> list:
        return ["steady_state"]

    def simulate(self, candidate):
        return self.simulator.run(candidate)

    def constraints(self) -> list:
        return [
            EngineeringConstraints.non_negative_params,
            EngineeringConstraints.component_mass_balance
        ]

    def outputs_of_interest(self) -> list:
        return [
            "component_balances",
            "violations"
        ]
