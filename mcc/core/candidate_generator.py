class CandidateGenerator:
    def generate(self, problem_state):
        # Evaluation mode: single given system
        if problem_state.mode == 'evaluate':
            return [{
                'id': 0,
                'model': 'given_system',
                'params': dict(problem_state.knowns)
            }]

        # Design mode WITHOUT bounds: structural candidate only
        if problem_state.mode == 'design' and not problem_state.design_bounds:
            return [{
                'id': 0,
                'model': 'design_structure',
                'params': dict(problem_state.knowns)
            }]

        # Design mode WITH bounds: sampling is REQUIRED
        if problem_state.mode == 'design' and problem_state.design_bounds:
            candidates = []
            n = 25
            for i in range(n):
                params = dict(problem_state.knowns)
                for var, (lo, hi) in problem_state.design_bounds.items():
                    params[var] = lo + (hi - lo) * (i / (n - 1))
                candidates.append({
                    'id': i,
                    'model': 'design_sample',
                    'params': params
                })
            return candidates

        return []
