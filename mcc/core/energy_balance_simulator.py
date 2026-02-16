class EnergyBalanceSimulator:
    def run(self, candidate):
        p = candidate['params']
        m = p['mass_flow']
        h_in = p['h_in']
        h_out = p['h_out']
        q = p['heat_duty']

        residual = m * (h_out - h_in) - q

        return {
            'mass_flow': m,
            'h_in': h_in,
            'h_out': h_out,
            'heat_duty': q,
            'energy_residual': residual
        }
