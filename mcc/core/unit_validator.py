from .unit_converter import UnitConverter, UnitConversionError

class UnitValidator:
    def validate(self, problem_state, domains):
        issues = []

        if not hasattr(problem_state, 'units'):
            return {
                'status': 'unit_error',
                'issues': [{
                    'type': 'missing_units_block',
                    'message': 'Units are required for all numeric parameters'
                }]
            }

        units = problem_state.units

        # 1) Every numeric known must have a unit
        for param, value in problem_state.knowns.items():
            if isinstance(value, (int, float)) and param not in units:
                issues.append({
                    'type': 'missing_unit',
                    'param': param,
                    'message': 'Numeric parameter has no unit'
                })

        # 2) Optional conversion (explicit opt-in)
        if getattr(problem_state, 'allow_unit_conversion', False):
            for domain in domains:
                expected = domain.expected_units()
                for param, expected_unit in expected.items():
                    if param in problem_state.knowns and param in units:
                        given_unit = units[param]
                        if given_unit != expected_unit:
                            if UnitConverter.can_convert(given_unit, expected_unit):
                                try:
                                    problem_state.knowns[param] = UnitConverter.convert_value(
                                        problem_state.knowns[param],
                                        given_unit,
                                        expected_unit
                                    )
                                    units[param] = expected_unit
                                except UnitConversionError as e:
                                    issues.append({
                                        'type': 'conversion_error',
                                        'param': param,
                                        'message': str(e)
                                    })

        # 3) Strict matching after conversion
        for domain in domains:
            expected = domain.expected_units()
            for param, expected_unit in expected.items():
                if param in problem_state.knowns:
                    given_unit = units.get(param)
                    if given_unit != expected_unit:
                        issues.append({
                            'type': 'unit_mismatch',
                            'param': param,
                            'given': given_unit,
                            'expected': expected_unit,
                            'domain': domain.domain_name()
                        })

        if issues:
            return {'status': 'unit_error', 'issues': issues}

        return None
