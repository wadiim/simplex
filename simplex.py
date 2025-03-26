"""
This file contains the implementation of the simplex method.
"""

class InvalidPivotRowIndex(Exception):
    pass


class InvalidPivotColumnIndex(Exception):
    pass


def get_pivot_col_idx(tableau: list[list[float]]) -> int:
    """
    Returns the index of the pivot column of a given tableau or -1 if there
    is no such column.
    """

    pivot_col_idx = -1
    for idx, val in enumerate(tableau[-1]):
        if val < 0 and (pivot_col_idx == -1 or val < tableau[-1][pivot_col_idx]):
            pivot_col_idx = idx

    return pivot_col_idx


# TODO: Merge `get_pivot_row_idx()` with `get_pivot_col_idx()` in order to
#       avoid checking if `pivot_col_idx` is valid.
def get_pivot_row_idx(tableau: list[list[float]], pivot_col_idx: int) -> int:
    """
    Returns the index of the pivot row of a given tableau or -1 if there is
    no such row.
    """

    # Calculate quotients
    # NOTE: Quotients that are 0, negative, or that have 0 in the denominator
    #       are ignored.
    if len(tableau) == 0 or len(tableau[0]) == 0:
        return -1

    try:
        quotients = [float('inf') for _ in range(len(tableau))]

        for idx in range(len(tableau)):
            numerator = tableau[idx][-1]
            denominator = tableau[idx][pivot_col_idx]
            if denominator == 0.0: continue

            val = numerator / denominator
            if val <= 0.0: continue

            quotients[idx] = val

        min_quotient_idx = 0
        for idx in range(len(quotients)):
            if quotients[idx] < quotients[min_quotient_idx]:
                min_quotient_idx = idx

        min_quotient = quotients[min_quotient_idx]
        return min_quotient_idx if min_quotient < float('inf') else -1
    except IndexError:
        raise InvalidPivotColumnIndex


# TODO: Make determining the pivot row and column indexes part of
#       `perform_pivoting()` instead of passing them as parameters in order
#       to avoid checking if they are valid.
def perform_pivoting(
        tableau: list[list[float]],
        pivot_row_idx: float,
        pivot_col_idx: float,
):
    """
    Performs pivoting on the tableau, i.e. a process of obtaining a 1 in the
    location of the pivot element, and then making all other entries 0 in the
    pivot column. The given tableau is modified in place.
    """

    if not (0 <= pivot_row_idx <= len(tableau)):
        raise InvalidPivotRowIndex

    try:
        # Make the pivot element a 1:
        pivot = tableau[pivot_row_idx][pivot_col_idx]
        tableau[pivot_row_idx] = [x/pivot for x in tableau[pivot_row_idx]]

        # Make all other entries 0 in the pivot column:
        for row_idx in range(len(tableau)):
            if row_idx == pivot_row_idx: continue

            multiplier = tableau[row_idx][pivot_col_idx]

            for col_idx, col_val in enumerate(tableau[row_idx]):
                pivot_row_val = tableau[pivot_row_idx][col_idx]
                tableau[row_idx][col_idx] = col_val - multiplier*pivot_row_val
    except IndexError:
        raise InvalidPivotColumnIndex


def is_basic(column: list[float]) -> bool:
    """
    Checks if the given column consists of all 0, except for a single 1.
    """
    return sum(column) == 1 and len([c for c in column if c == 0]) == len(column) - 1


def get_solution(tableau: list[list[float]]) -> tuple[list[float], float]:
    """
    Returns the solution and it's objective function value in the following
    form: ([x1, x2, ..., xn], v), where x1, x2, ..., xn are values of the
    non-slack variables and v is the value of the objective function in that
    point. It is assumed that the given tableau is optimal.
    """

    solution = []
    for col_idx in range(len(tableau[:-1])):
        column = [tableau[r][col_idx] for r in range(len(tableau))]
        partial_solution = 0
        if is_basic(column):
            one_index = column.index(1)
            partial_solution = tableau[one_index][-1]
        solution.append(partial_solution)

    return solution, tableau[-1][-1]


def perform_simplex(tableau: list[list[float]]) -> tuple[list[float], float]:
    """
    Returns the solution for the given tableau.
    """

    while True:
        pivot_col_idx = get_pivot_col_idx(tableau)
        if pivot_col_idx == -1: break

        pivot_row_idx = get_pivot_row_idx(tableau, pivot_col_idx)
        if pivot_row_idx == -1: break

        perform_pivoting(tableau, pivot_row_idx, pivot_col_idx)

    return get_solution(tableau)


def to_tableau(
        goal_function: list[float],
        constraints: list[list[float]],
) -> list[list[float]]:
    """
    Returns a tableau for the given goal function and constraints.
    """
    # TODO: Add more details to the docstring.

    result = []
    var_count = len(goal_function)

    for i, constraint in enumerate(constraints):
        new_row = constraint[:-1]

        # Add slack variables
        for j in range(var_count+1):
            new_row.append(1 if j == i else 0)

        new_row.append(constraint[-1])
        result.append(new_row)

    bottom_row = [-x for x in goal_function]
    for i in range(var_count):
        bottom_row.append(0)
    bottom_row.append(1)
    bottom_row.append(0)
    result.append(bottom_row)

    return result
