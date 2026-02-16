class ProblemState:
    def __init__(
        self,
        goal: str,
        parameters: dict = None,
        knowns: dict = None,
        unknowns: dict = None,
        assumptions: list = None,
        domains: list = None,
        units: dict = None,
        criteria: dict = None
    ):
        # Canonical fields (used by MCC)
        self.goal = goal
        self.parameters = (
            parameters
            if parameters is not None
            else (knowns if knowns is not None else {})
        )
        self.assumptions = assumptions or []
        self.domains = domains or []
        self.units = units or {}

        # Optional / explanatory fields (LLM-facing)
        self.criteria = criteria or {}
        self.unknowns = unknowns or {}

    def get(self, key, default=None):
        return getattr(self, key, default)
