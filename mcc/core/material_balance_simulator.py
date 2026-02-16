from .simulation_interface import Simulator, SimulationResult

class MaterialBalanceSimulator(Simulator):
    def run(self, candidate):
        params = candidate.get("params", {})

        # Expecting inlet and outlet flow rates
        inlet = params.get("inlet_flow")
        outlet = params.get("outlet_flow")

        if inlet is None or outlet is None:
            return SimulationResult(outputs={})

        accumulation = inlet - outlet

        outputs = {
            "inlet_flow": inlet,
            "outlet_flow": outlet,
            "accumulation": accumulation
        }

        return SimulationResult(outputs=outputs)
