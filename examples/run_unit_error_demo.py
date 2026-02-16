import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

ps = ProblemState(
    goal='unit_mismatch_demo',
    knowns={
        'mass_flow': 2.0,
        'h_in': 100.0,
        'h_out': 150.0,
        'heat_duty': 100.0
    },
    assumptions=['steady_state', 'no_shaft_work', 'no_ke_pe_change'],
    criteria={}
)

# INTENTIONALLY WRONG UNITS
ps.units = {
    'mass_flow': 'kg/h',      # should be kg/s
    'h_in': 'kJ/kg',
    'h_out': 'kJ/kg',
    'heat_duty': 'kJ/s'
}

mcc = MinimalCognitiveCore()
print(mcc.solve(ps))
