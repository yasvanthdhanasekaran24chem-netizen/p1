class EngineeringConstraints:

    @staticmethod
    def non_negative_params(candidate, sim_outputs=None):
        for v in candidate['params'].values():
            if isinstance(v, (int, float)) and v < 0:
                return False
        return True

    @staticmethod
    def steady_state_energy_balance(candidate, sim_outputs):
        # tolerance-based check
        residual = sim_outputs.get('energy_residual', None)
        if residual is None:
            return False
        return abs(residual) <= 1e-6
