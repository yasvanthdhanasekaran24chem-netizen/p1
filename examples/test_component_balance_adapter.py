import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.component_mass_balance_domain import ComponentMassBalanceDomain

domain = ComponentMassBalanceDomain()

candidate = {
    "params": {
        "inlet_components": {
            "A": 50.0,
            "B": 30.0
        },
        "outlet_components": {
            "A": 50.0,
            "B": 30.0
        }
    }
}

sim_result = domain.simulate(candidate)
constraints = domain.constraints()

print("Domain:", domain.domain_name())
print("Simulation outputs:", sim_result.outputs)

for rule in constraints:
    print(rule.__name__, "->", rule(candidate, sim_result.outputs))
