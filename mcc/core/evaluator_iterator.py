class EvaluatorIterator:
    def __init__(self, validator, scorer, simulator):
        self.validator = validator
        self.scorer = scorer
        self.simulator = simulator

    def run(self, candidates, problem_state):
        best_candidate = None
        best_score = float('-inf')
        best_outputs = None
        best_breakdown = None

        for i, candidate in enumerate(candidates):
            # 1. Run simulation FIRST
            sim_outputs = self.simulator.simulate(candidate)

            # 2. Validate constraints WITH sim_outputs
            if not self.validator.validate(candidate, sim_outputs):
                continue

            # 3. Score candidate
            score, breakdown = self.scorer.score(candidate, sim_outputs)

            if score > best_score:
                best_score = score
                best_candidate = candidate
                best_outputs = sim_outputs
                best_breakdown = breakdown

        return {
            'status': 'provisional',
            'best_candidate': best_candidate,
            'score': best_score,
            'score_breakdown': best_breakdown,
            'simulation_outputs': best_outputs,
            'iterations': len(candidates)
        }
