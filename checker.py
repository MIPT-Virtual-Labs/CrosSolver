from utils import get_size_error
from constants import (
    CORRECT,
    ERRORS,
    FIELD,
    ERROR,
    LIST_TYPE_ERROR,
    MASSES,
    NAMES,
    EQUATIONS,
    CORRECT_DICT
)


def get_error_configuration(error, field):
    return {
        CORRECT: False,
        ERRORS: [{
            ERROR: error,
            FIELD: field
        }]
    }


def check_arguments(names: list, masses: list, equations: list) -> dict:
    if type(names) != list:
        return get_error_configuration(LIST_TYPE_ERROR, NAMES)
    if type(masses) != list:
        return get_error_configuration(LIST_TYPE_ERROR, MASSES)
    if type(equations) != list:
        return get_error_configuration(LIST_TYPE_ERROR, EQUATIONS)

    n = len(names)
    if n != len(masses):
        return get_error_configuration(get_size_error(n), MASSES)
    if n != len(equations):
        return get_error_configuration(get_size_error(n), EQUATIONS)

    return CORRECT_DICT
