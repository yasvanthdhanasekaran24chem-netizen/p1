from .domain_adapter import DomainAdapter
from .engineering_constraints import EngineeringConstraints

class EnergyBalanceDomain(DomainAdapter):
    def domain_name(self):
        return 'energy_balance'

    def required_parameters(self):
        return ['mass_flow', 'h_in', 'h_out', 'heat_duty']

    def required_assumptions(self):
        return ['steady_state', 'no_shaft_work', 'no_ke_pe_change']

    def expected_units(self):
        return {
            'mass_flow': 'kg/s',
            'h_in': 'kJ/kg',
            'h_out': 'kJ/kg',
            'heat_duty': 'kJ/s'
        }

    def project_unknowns(self, params):
        if 'heat_duty' not in params:
            params = dict(params)
            params['heat_duty'] = params['mass_flow'] * (params['h_out'] - params['h_in'])
        return params

    def simulate(self, candidate):
        p = candidate['params']
        residual = p['mass_flow'] * (p['h_out'] - p['h_in']) - p['heat_duty']
        return {
            'mass_flow': p['mass_flow'],
            'h_in': p['h_in'],
            'h_out': p['h_out'],
            'heat_duty': p['heat_duty'],
            'energy_residual': residual
        }

    def constraints(self):
        return [
            EngineeringConstraints.non_negative_params,
            EngineeringConstraints.steady_state_energy_balance
        ]

    def outputs_of_interest(self):
        return ['energy_residual']
