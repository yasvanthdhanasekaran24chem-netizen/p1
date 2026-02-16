from .assumption_conflicts import AssumptionConflicts

class AssumptionValidator:
    def validate(self, problem_state):
        conflicts = AssumptionConflicts.find_conflicts(problem_state.assumptions)

        if conflicts:
            return {
                "status": "assumption_conflict",
                "conflicts": conflicts
            }

        return None
