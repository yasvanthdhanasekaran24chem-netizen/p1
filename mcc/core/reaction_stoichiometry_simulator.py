class ReactionStoichiometrySimulator:
    def run(self, candidate):
        p = candidate['params']

        # Feed (mol/s)
        FA0 = p['FA0']   # A feed
        FB0 = p.get('FB0', 0.0)

        # Extents (design variables)
        xi1 = p['xi1']   # A -> B
        xi2 = p['xi2']   # A -> C (undesired)

        # Outlet flows
        FA = FA0 - xi1 - xi2
        FB = FB0 + xi1
        FC = xi2

        # Metrics
        conversion = (FA0 - FA) / FA0 if FA0 > 0 else 0.0
        selectivity = FB / (FC + 1e-12)

        return {
            'FA': FA,
            'FB': FB,
            'FC': FC,
            'conversion': conversion,
            'selectivity': selectivity
        }
