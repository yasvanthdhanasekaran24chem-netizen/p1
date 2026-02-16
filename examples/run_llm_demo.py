import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcc.llm.llm_wrapper import LLMWrapper
from mcc.core.problem_state import ProblemState
from mcc.core.mcc import MinimalCognitiveCore
from mcc.core.engineering_constraints import EngineeringConstraints

llm = LLMWrapper()

# Step 1: Human intent
user_input = "Design a simple system with two parameters"

intent = llm.interpret_intent(user_input)

ps = ProblemState(
    goal=intent["goal"],
    knowns={"a": 3, "b": 4},
    unknowns=[],
    constraints=["non_negative"],
    assumptions=["steady_state"],
    criteria={"objectives": ["simplicity", "robustness"]}
)

rules = [EngineeringConstraints.non_negative_params]

mcc = MinimalCognitiveCore(rules=rules)

result = mcc.solve(ps)

# Step 2: Language explanation
explanation = llm.explain_result(result)

print("MCC RESULT:")
print(result)
print("\nLLM EXPLANATION:")
print(explanation)
