import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

ps = ProblemState(
    goal='reaction_design',
    knowns={
        'FA0': 100.0
    },
    unknowns=['xi1', 'xi2'],
    assumptions=['steady_state', 'isothermal'],
    criteria={
        'conversion': 'maximize',
        'selectivity': 'maximize'
    }
)

ps.units = {
    'FA0': 'mol/s',
    'xi1': 'mol/s',
    'xi2': 'mol/s'
}

ps.mode = 'design'
ps.allow_unit_conversion = False

# Design space
ps.design_bounds = {
    'xi1': (0.0, 90.0),
    'xi2': (0.0, 90.0)
}

mcc = MinimalCognitiveCore(objective_weights={
    'conversion': 0.6,
    'selectivity': 0.4
})

print(mcc.solve(ps))
