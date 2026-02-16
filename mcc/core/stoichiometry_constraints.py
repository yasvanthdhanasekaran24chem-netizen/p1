class StoichiometryConstraints:

    @staticmethod
    def non_negative_flows(candidate, sim_outputs):
        return (
            sim_outputs['FA'] >= 0 and
            sim_outputs['FB'] >= 0 and
            sim_outputs['FC'] >= 0
        )

    @staticmethod
    def extents_feasible(candidate, sim_outputs):
        p = candidate['params']
        return p['xi1'] >= 0 and p['xi2'] >= 0
