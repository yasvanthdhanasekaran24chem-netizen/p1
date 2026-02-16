import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

ps = ProblemState(
    goal='pareto_energy_design',
    knowns={
        'mass_flow': 2.0,   # kg/h (will convert)
        'h_in': 100.0,
        'h_out': 150.0
    },
    unknowns=['heat_duty'],
    assumptions=['steady_state', 'no_shaft_work', 'no_ke_pe_change'],
    criteria={}
)

ps.units = {
    'mass_flow': 'kg/h',
    'h_in': 'kJ/kg',
    'h_out': 'kJ/kg',
    'heat_duty': 'kJ/s'
}

ps.allow_unit_conversion = True
ps.mode = 'design'

# Search bounds for design variable
ps.design_bounds = {
    'heat_duty': (0.0, 1.0)   # kJ/s
}

mcc = MinimalCognitiveCore(objective_weights={
    'simplicity': 0.3,
    'robustness': 0.7
})

print(mcc.solve(ps))
