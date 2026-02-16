from .register_domains import registry

class GapAnalyzer:
    def analyze(self, problem_state):
        gaps = []

        # Missing known parameters
        if not problem_state.knowns:
            gaps.append({
                "type": "missing_inputs",
                "items": ["No known parameters provided"]
            })

        # Determine applicable domains
        applicable_domains = registry.applicable_domains(problem_state)

        if not applicable_domains:
            gaps.append({
                "type": "no_applicable_domains",
                "items": ["No domain matches given parameters and assumptions"]
            })
            return gaps

        # Check if any applicable domain provides constraints
        domain_constraints = []
        for domain in applicable_domains:
            domain_constraints.extend(domain.constraints())

        if not domain_constraints:
            gaps.append({
                "type": "missing_constraints",
                "items": ["Applicable domains define no constraints"]
            })

        # Missing assumptions (soft warning)
        if not problem_state.assumptions:
            gaps.append({
                "type": "missing_assumptions",
                "items": ["No assumptions explicitly stated"]
            })

        return gaps
