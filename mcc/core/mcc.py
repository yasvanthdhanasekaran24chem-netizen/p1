from .problem_state import ProblemState
from .candidate_generator import CandidateGenerator
from .evaluator_iterator import EvaluatorIterator
from .constraint_validator import ConstraintValidator
from .assumption_validator import AssumptionValidator
from .persistent_memory import PersistentMemory


class MinimalCognitiveCore:
    def __init__(self, objective_weights=None):
        self.generator = CandidateGenerator()
        self.validator = ConstraintValidator()
        self.assumption_validator = AssumptionValidator()
        self.memory = PersistentMemory()
        self.objective_weights = objective_weights or {}

    def solve(self, problem_state: ProblemState):
        # 1. Validate assumptions
        assumption_issue = self.assumption_validator.validate(problem_state)
        if assumption_issue:
            return assumption_issue

        results = {}

        for domain in problem_state.domains:
            # 2. Generate candidates
            candidates = self.generator.generate(problem_state)

            evaluator = EvaluatorIterator(
                domain=domain,
                constraints=self.validator,
                objective_weights=self.objective_weights
            )

            domain_result = evaluator.run(candidates, problem_state)
            results[domain.domain_name()] = domain_result

            # 3. Store memory ONLY if result is meaningful
            if (
                domain_result.get('status') == 'provisional'
                and domain_result.get('best_candidate') is not None
            ):
                self.memory.store(
                    domain=domain.domain_name(),
                    goal=problem_state.goal,
                    params=domain_result['best_candidate']['params'],
                    outputs=domain_result.get('simulation_outputs')
                )

        return {
            'status': 'completed',
            'domains_executed': list(results.keys()),
            'results': results
        }
