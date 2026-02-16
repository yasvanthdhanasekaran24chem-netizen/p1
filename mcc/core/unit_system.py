class UnitSystem:
    # Base dimensions: M (mass), L (length), T (time), E (energy)

    UNITS = {
        'kg': {'M': 1},
        'kg/s': {'M': 1, 'T': -1},
        'kg/h': {'M': 1, 'T': -1},
        'J': {'E': 1},
        'kJ': {'E': 1},
        'J/kg': {'E': 1, 'M': -1},
        'kJ/kg': {'E': 1, 'M': -1},
        'kJ/s': {'E': 1, 'T': -1}
    }

    @classmethod
    def dims(cls, unit):
        return cls.UNITS.get(unit)

    @classmethod
    def compatible(cls, given, expected):
        # Strict mode: units must match exactly
        return given == expected
