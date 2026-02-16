from .domain_registry import DomainRegistry
from .reaction_stoichiometry_domain import ReactionStoichiometryDomain

registry = DomainRegistry()
registry.register(ReactionStoichiometryDomain())
