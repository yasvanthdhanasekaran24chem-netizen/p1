class AssumptionConflicts:

    CONFLICTS = {
        "steady_state": {"dynamic"},
        "dynamic": {"steady_state"},
        "ideal_gas": {"real_fluid"},
        "real_fluid": {"ideal_gas"},
        "incompressible": {"compressible"},
        "compressible": {"incompressible"}
    }

    @classmethod
    def find_conflicts(cls, assumptions):
        conflicts = []
        assumption_set = set(assumptions)

        for a in assumption_set:
            incompatible = cls.CONFLICTS.get(a, set())
            for b in incompatible:
                if b in assumption_set:
                    conflicts.append((a, b))

        return conflicts
