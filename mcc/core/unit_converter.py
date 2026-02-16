class UnitConversionError(Exception):
    pass


class UnitConverter:
    # Exact, auditable conversion factors
    # (from_unit, to_unit) -> multiplier
    CONVERSIONS = {
        ('kg/h', 'kg/s'): 1.0 / 3600.0,
        ('kg/s', 'kg/h'): 3600.0,
        ('J', 'kJ'): 1.0 / 1000.0,
        ('kJ', 'J'): 1000.0
    }

    @classmethod
    def can_convert(cls, from_unit, to_unit):
        return (from_unit, to_unit) in cls.CONVERSIONS

    @classmethod
    def convert_value(cls, value, from_unit, to_unit):
        key = (from_unit, to_unit)
        if key not in cls.CONVERSIONS:
            raise UnitConversionError(f'No conversion from {from_unit} to {to_unit}')
        return value * cls.CONVERSIONS[key]
