class ConstraintValidator:
    def __init__(self, rules=None):
        # rules are callables: (candidate, sim_outputs) -> bool
        self.rules = rules or []

    def validate(self, candidate, sim_outputs):
        for rule in self.rules:
            if not rule(candidate, sim_outputs):
                return {
                    'status': 'constraint_violation',
                    'failed_rule': rule.__name__
                }
        return None
