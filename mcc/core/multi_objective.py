class MultiObjectiveScorer:
    def __init__(self, weights):
        self.weights = weights

    def score(self, candidate, sim_outputs):
        total = 0.0
        breakdown = {}

        for metric, weight in self.weights.items():
            value = sim_outputs.get(metric, 0.0)
            total += weight * value
            breakdown[metric] = value

        return total, breakdown
