
import re


def to_snake_case(value: str) -> str:
    """Convert a CamelCase or camelCase string to snake_case.

    Parameters
    ----------
    value : str
        The string in CamelCase or camelCase format.

    Returns
    -------
    str
        The converted string in snake_case format.
    Ejemplos:
    >>> to_snake_case("CamelCase")
    'camel_case'
    >>> to_snake_case("myVariableName")
    'my_variable_name'
    """
    if not isinstance(value, str):
        raise ValueError("Cannot convert value to snake_case")
    parts = value.split('_')
    converted = []

    for part in parts:
        if not part:  # handle double underscores or leading/trailing
            converted.append('')
            continue
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', part)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        converted.append(s2.lower())

    return '_'.join(converted)

