import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.register_domains import registry
from mcc.core.problem_state import ProblemState
from mcc.core.unit_validator import UnitValidator

print('--- REGISTERED DOMAINS ---')
for d in registry.list_domains():
    print(d.domain_name(), 'expected_units =', d.expected_units())

ps = ProblemState(
    goal='debug_units',
    knowns={
        'mass_flow': 2.0,
        'h_in': 100.0,
        'h_out': 150.0,
        'heat_duty': 100.0
    },
    assumptions=['steady_state', 'no_shaft_work', 'no_ke_pe_change'],
    criteria={}
)

ps.units = {
    'mass_flow': 'kg/h',
    'h_in': 'kJ/kg',
    'h_out': 'kJ/kg',
    'heat_duty': 'kJ/s'
}

print('\\n--- PROBLEM UNITS ---')
print(ps.units)

validator = UnitValidator()
print('\\n--- VALIDATOR RESULT ---')
print(validator.validate(ps, registry.list_domains()))
