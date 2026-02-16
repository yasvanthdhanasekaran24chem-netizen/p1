class DomainRegistry:
    def __init__(self):
        self._domains = []

    def register(self, domain):
        self._domains.append(domain)

    def list_domains(self):
        return list(self._domains)

    def applicable_domains(self, problem_state):
        applicable = []

        for domain in self._domains:
            required = set(domain.required_parameters())
            knowns = set(problem_state.knowns.keys())
            unknowns = set(getattr(problem_state, 'unknowns', []))

            if problem_state.mode == 'design':
                if required.issubset(knowns.union(unknowns)):
                    applicable.append(domain)
            else:
                if required.issubset(knowns):
                    applicable.append(domain)

        return applicable
