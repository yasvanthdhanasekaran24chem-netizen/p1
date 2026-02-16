from .simulation_interface import Simulator, SimulationResult

class ComponentMassBalanceSimulator(Simulator):
    def run(self, candidate):
        p = candidate.get("params", {})

        # Expect species-wise inlet & outlet dicts
        inlet = p.get("inlet_components")
        outlet = p.get("outlet_components")

        if inlet is None or outlet is None:
            return SimulationResult(outputs={})

        outputs = {
            "component_balances": {},
            "violations": []
        }

        all_species = set(inlet.keys()) | set(outlet.keys())

        for comp in all_species:
            Fin = inlet.get(comp, 0.0)
            Fout = outlet.get(comp, 0.0)
            balance = Fin - Fout

            outputs["component_balances"][comp] = balance

            if abs(balance) > 1e-6:
                outputs["violations"].append(comp)

        return SimulationResult(outputs=outputs)
