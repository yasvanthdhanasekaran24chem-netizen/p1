import math

class ParetoOptimizer:
    def __init__(self, samples=50):
        self.samples = samples

    def sample_candidates(self, problem_state):
        candidates = []
        base = dict(problem_state.knowns)

        for i in range(self.samples):
            params = dict(base)
            for var, (lo, hi) in problem_state.design_bounds.items():
                if self.samples == 1:
                    params[var] = lo
                else:
                    params[var] = lo + (hi - lo) * (i / (self.samples - 1))
            candidates.append({
                'id': i,
                'model': 'design_sample',
                'params': params
            })

        return candidates

    @staticmethod
    def dominates(a, b):
        better_or_equal = all(a[k] >= b[k] for k in a)
        strictly_better = any(a[k] > b[k] for k in a)
        return better_or_equal and strictly_better

    def pareto_front(self, scored):
        front = []
        for i, (ci, si) in enumerate(scored):
            dominated = False
            for j, (cj, sj) in enumerate(scored):
                if i != j and self.dominates(sj, si):
                    dominated = True
                    break
            if not dominated:
                front.append((ci, si))
        return front
