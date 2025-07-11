"""
This file contains the implementation of the simplex method.
"""

from enum import Enum, auto
from termcolor import colored


class Mode(Enum):
    MINIMIZATION = auto(),
    MAXIMIZATION = auto(),


def get_pivot_pos(tableau: list[list[float]]) -> tuple[int, int] | None:
    """
    Returns the position of the pivot element or None if there is no such
    element.
    """

    # Find column position
    col_idx = None
    for idx, val in enumerate(tableau[-1]):
        if val >= 0: continue
        if col_idx == None or val < tableau[-1][col_idx]:
            col_idx = idx

    if col_idx == None: return None

    # Find row position
    quotients = [float('inf') for _ in range(len(tableau))]
    for idx in range(len(tableau)):
        numerator = tableau[idx][-1]
        denominator = tableau[idx][col_idx]
        if denominator == 0.0: continue
        val = numerator / denominator
        if val <= 0.0: continue
        quotients[idx] = val
    row_idx = 0
    for idx in range(len(quotients)):
        if quotients[idx] < quotients[row_idx]:
            row_idx = idx

    if quotients[row_idx] == float('inf'): return None

    return (row_idx, col_idx)


def perform_pivoting(tableau: list[list[float]]) -> bool:
    """
    Performs pivoting on the tableau, i.e. a process of obtaining a 1 in the
    location of the pivot element, and then making all other entries 0 in the
    pivot column. The given tableau is modified in place.
    """

    pos = get_pivot_pos(tableau)
    if pos == None: return False
    pivot_row_idx, pivot_col_idx = pos

    print(tableau_to_str(tableau, pivot_pos=pos))

    # Make the pivot element a 1:
    pivot = tableau[pivot_row_idx][pivot_col_idx]
    tableau[pivot_row_idx] = [x/pivot for x in tableau[pivot_row_idx]]

    print(tableau_to_str(tableau))

    # Make all other entries 0 in the pivot column:
    for row_idx in range(len(tableau)):
        if row_idx == pivot_row_idx: continue

        multiplier = tableau[row_idx][pivot_col_idx]

        for col_idx, col_val in enumerate(tableau[row_idx]):
            pivot_row_val = tableau[pivot_row_idx][col_idx]
            tableau[row_idx][col_idx] = col_val - multiplier*pivot_row_val

    return True


def is_basic(column: list[float]) -> bool:
    """
    Checks if the given column consists of all 0, except for a single 1.
    """
    return sum(column) == 1 and len([c for c in column if c == 0]) == len(column) - 1


def get_solution(
        tableau: list[list[float]],
        mode = Mode.MAXIMIZATION,
) -> tuple[list[float], float]:
    """
    Returns the solution and it's objective function value in the following
    form: ([x1, x2, ..., xn], v), where x1, x2, ..., xn are values of the
    non-slack variables and v is the value of the objective function in that
    point. It is assumed that the given tableau is optimal.
    """

    solution = []
    sol_idxs = set()

    if mode == Mode.MINIMIZATION:
        var_count = len(tableau) - 1
        var_start_idx = len(tableau[-1]) - var_count - 2
        sol_idxs.add((var_start_idx, len(tableau) - 1))
        for i in range(var_count):
            solution.append(tableau[-1][var_start_idx + i])
            sol_idxs.add((len(tableau) - 1, var_start_idx + i))
    else:
        for col_idx in range(len(tableau[:-1])):
            column = [tableau[r][col_idx] for r in range(len(tableau))]
            partial_solution = 0
            if is_basic(column):
                one_index = column.index(1)
                partial_solution = tableau[one_index][-1]
                sol_idxs.add((one_index, len(tableau[one_index]) - 1))
            solution.append(partial_solution)

    sol_idxs.add((len(tableau) - 1, len(tableau[-1]) - 1))
    print(tableau_to_str(tableau, sol_idxs=sol_idxs))
    print(f"f({", ".join([str(x) for x in solution])}) = {tableau[-1][-1]}\n")
    return solution, tableau[-1][-1]


def can_be_improved(tableau: list[list[float]]) -> bool:
    z = tableau[-1]
    return any(x < 0 for x in z[:-1])


def perform_simplex(
        tableau: list[list[float]],
        mode = Mode.MAXIMIZATION,
) -> tuple[list[float], float]:
    """
    Returns the solution for the given tableau.
    """

    while can_be_improved(tableau):
        if not perform_pivoting(tableau):
            return (
                [float('inf') for _ in range(len(tableau[:-1]))],
                float('inf'),
            )

    return get_solution(tableau, mode)


def to_tableau(
        goal_function: list[float],
        constraints: list[list[float]],
        mode = Mode.MAXIMIZATION,
) -> list[list[float]]:
    """
    Returns a tableau for the given goal function and constraints.
    The `goal_function` is the list of subsequent goal function's
    coefficients, e.g. [3, 2, 5] represents the following function:
    Z = 3*x1 + 2*x2 + 5*x3. `constraints` is the list of constraints, where
    each item is a list of coefficients of the according constraint and the
    free term as the last element, e.g. [2, 1, 7, 12] represents the
    following constraint: 2*x1 + 1*x2 + 7*x3 <= 12.
    """

    result = []
    if mode == Mode.MINIMIZATION:
        for i in range(len(constraints)):
            # `<=` -> `>=`
            constraints[i] = [-x for x in constraints[i]]
        matrix = to_basic_matrix(goal_function, constraints)
        print(tableau_to_str(matrix))
        matrix = transpose_basic_matrix(matrix)
        print(tableau_to_str(matrix))
        result = basic_matrix_to_tableau(matrix)
    else:
        for i, constraint in enumerate(constraints):
            new_row = constraint[:-1]

            # Add slack variables
            new_row += [1 if j == i else 0 for j in range(len(constraints) + 1)]

            new_row.append(constraint[-1])
            result.append(new_row)

        bottom_row =  [-x for x in goal_function]
        bottom_row += [0 for _ in range(len(constraints))]
        bottom_row += [1, 0]
        result.append(bottom_row)

    return result


def to_basic_matrix(
        goal_function: list[float],
        constraints: list[list[float]],
) -> list[list[float]]:
    result = []

    for constraint in constraints:
        result.append(constraint)
    result.append(goal_function + [0])

    return result


def transpose_basic_matrix(matrix: list[list[float]]) -> list[list[float]]:
    result = [[] for _ in range(len(matrix[0]))]

    for row in matrix:
        for i, val in enumerate(row):
            result[i].append(val)

    return result


def basic_matrix_to_tableau(
        matrix: list[list[float]],
) -> list[list[float]]:
    result = []
    height = len(matrix)

    for i, row in enumerate(matrix):
        result.append(row[:-1] if i < len(matrix) - 1 else [-x for x in row[:-1]])
        result[-1] += [1 if j == i else 0 for j in range(height)]
        result[-1].append(row[-1])

    return result


def calc_num_widths(num: float) -> tuple[int, int]:
    num_str_parts = str(num).split('.')
    real_len = len(num_str_parts[0])
    frac_len = len(num_str_parts[1]) if len(num_str_parts) > 1 else 0

    return (real_len, frac_len)


def calc_col_widths(tableau: list[list[float]]) -> list[int]:
    widths = []

    if len(tableau) > 0 and len(tableau[0]) == 0:
        return [(0, 0)]

    for row in tableau:
        for i, val in enumerate(row):
            real_len, frac_len = calc_num_widths(val)
            while len(widths) <= i:
                widths.append((real_len, frac_len))
            if real_len > widths[i][0]:
                widths[i] = (real_len, widths[i][1])
            if frac_len > widths[i][1]:
                widths[i] = (widths[i][0], frac_len)

    return widths


def tableau_to_str(tableau: list[list[float]], **kwargs):
    widths = calc_col_widths(tableau)
    total_width = 0
    for w in widths:
        total_width += w[0] + w[1] + (1 if w[1] > 0 else 0)
    total_width += (len(widths) - 1) * len(", ")
    total_width = max(1, total_width)

    ret = "┌" + (" "*total_width) + "┐\n"
    if len(tableau) > 0 and len(tableau[0]) > 0:
        for i, row in enumerate(tableau):
            ret += "│"
            row_strs = []
            for j, v in enumerate(row):
                real_len, frac_len = calc_num_widths(v)
                if 'sol_idxs' in kwargs and (i, j) in kwargs['sol_idxs']:
                    row_strs.append(
                            colored(
                                (" "*(widths[j][0] - real_len))
                                + f"{v:.{widths[j][1]}f}",
                                'black', 'on_blue'
                            )
                    )
                else:
                    row_strs.append(
                            (" "*(widths[j][0] - real_len))
                            + f"{v:.{widths[j][1]}f}"
                    )
            if 'pivot_pos' in kwargs and i == kwargs['pivot_pos'][0]:
                ret += colored(", ".join(s for s in row_strs), 'black', 'on_blue')
            else:
                ret += ", ".join([colored(s, 'black', 'on_blue')
                    if 'pivot_pos' in kwargs and k == kwargs['pivot_pos'][1]
                    else s for k, s in enumerate(row_strs)]
                )
            ret += "│\n"
    ret += "└" + (" "*total_width) + "┘"

    return ret
