from .simulation_interface import Simulator, SimulationResult

class MultiStreamMassBalanceSimulator(Simulator):
    def run(self, candidate):
        p = candidate.get("params", {})

        F1 = p.get("F1")
        F2 = p.get("F2")
        Fo1 = p.get("Fo1")
        Fo2 = p.get("Fo2")

        if None in (F1, F2, Fo1, Fo2):
            return SimulationResult(outputs={})

        Fm = F1 + F2

        outputs = {
            "F1": F1,
            "F2": F2,
            "Fm": Fm,
            "Fo1": Fo1,
            "Fo2": Fo2,
            "mixer_balance": F1 + F2 - Fm,
            "splitter_balance": Fm - (Fo1 + Fo2)
        }

        return SimulationResult(outputs=outputs)
