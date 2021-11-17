from utils import get_size_error
# from local_constants import (
#     CORRECT,
#     ERRORS,
#     FIELD,
#     ERROR,
#     LIST_TYPE_ERROR,
#     MASSES,
#     NAMES,
#     EQUATIONS,
#     CORRECT_DICT
# )
import local_constants as C


def get_error_configuration(error, field):
    return {
        C.CORRECT: False,
        C.ERRORS: [{
            C.ERROR: error,
            C.FIELD: field
        }]
    }


def check_arguments(t, steps_amount: int, names: list, masses: list, equations: list) -> dict:
    if not (type(t) == int or type(t) == float):
        return get_error_configuration(C.NUMBER_TIME_ERROR, C.TIME)
    if not type(steps_amount) == int:
        return get_error_configuration(C.INT_STEPS_ERROR, C.STEPS_AMOUNT)
    if steps_amount > C.CRITICAL_STEPS_AMOUNT:
        return get_error_configuration(C.TOO_MANY_STEPS_AMOUNT, C.STEPS_AMOUNT)
    if type(names) != list:
        return get_error_configuration(C.LIST_TYPE_ERROR, C.NAMES)
    if type(masses) != list:
        return get_error_configuration(C.LIST_TYPE_ERROR, C.MASSES)
    if type(equations) != list:
        return get_error_configuration(C.LIST_TYPE_ERROR, C.EQUATIONS)

    n = len(names)
    if n != len(masses):
        return get_error_configuration(get_size_error(n), C.MASSES)
    if n != len(equations):
        return get_error_configuration(get_size_error(n), C.EQUATIONS)

    return C.CORRECT_DICT
