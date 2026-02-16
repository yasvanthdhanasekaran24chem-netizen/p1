class SimulationResult:
    def __init__(self, outputs):
        self.outputs = outputs


class Simulator:
    def run(self, candidate):
        raise NotImplementedError("Simulator must implement run()")
