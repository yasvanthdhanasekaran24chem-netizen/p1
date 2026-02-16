import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.energy_balance_domain import EnergyBalanceDomain

domain = EnergyBalanceDomain()

candidate = {
    "params": {
        "mass_flow": 2.0,
        "h_in": 100.0,
        "h_out": 150.0,
        "heat_duty": 100.0
    }
}

sim_result = domain.simulate(candidate)
constraints = domain.constraints()

print("Domain:", domain.domain_name())
print("Simulation outputs:", sim_result.outputs)

for rule in constraints:
    print(rule.__name__, "->", rule(candidate, sim_result.outputs))
