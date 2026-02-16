from .domain_adapter import DomainAdapter
from .material_balance_simulator import MaterialBalanceSimulator
from .engineering_constraints import EngineeringConstraints

class MassBalanceDomain(DomainAdapter):
    def __init__(self):
        self.simulator = MaterialBalanceSimulator()

    def domain_name(self) -> str:
        return "mass_balance"

    def required_parameters(self) -> list:
        return ["inlet_flow", "outlet_flow"]

    def required_assumptions(self) -> list:
        return ["steady_state"]

    def simulate(self, candidate):
        return self.simulator.run(candidate)

    def constraints(self) -> list:
        return [
            EngineeringConstraints.non_negative_params,
            EngineeringConstraints.steady_state_mass_balance
        ]

    def outputs_of_interest(self) -> list:
        return [
            "inlet_flow",
            "outlet_flow",
            "accumulation"
        ]
