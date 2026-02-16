from .simulation_interface import Simulator, SimulationResult
import math

class SimpleNumericSimulator(Simulator):
    def run(self, candidate):
        params = candidate.get("params", {})
        values = list(params.values())

        if not values:
            return SimulationResult(outputs={})

        outputs = {
            "sum": sum(values),
            "product": math.prod(values),
            "magnitude": math.sqrt(sum(v*v for v in values))
        }

        return SimulationResult(outputs=outputs)
