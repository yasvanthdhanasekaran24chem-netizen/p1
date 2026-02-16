import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.llm.cognitive_assistant import CognitiveAssistant
from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore

assistant = CognitiveAssistant()

ps = ProblemState(
    goal='reaction_design',
    knowns={'FA0': 100.0},
    unknowns=['xi1', 'xi2'],
    assumptions=['steady_state', 'isothermal'],
    criteria={'conversion': 'maximize', 'selectivity': 'maximize'}
)

ps.units = {'FA0': 'mol/s', 'xi1': 'mol/s', 'xi2': 'mol/s'}
ps.mode = 'design'
ps.design_bounds = {'xi1': (0, 90), 'xi2': (0, 90)}

# IMPORTANT: objective weights
assistant.mcc = MinimalCognitiveCore(objective_weights={
    'conversion': 0.6,
    'selectivity': 0.4
})

response = assistant.solve_from_text(
    "Design a reactor to maximize conversion and selectivity",
    ps
)

print('--- EXPLANATION ---')
print(response['explanation'])
