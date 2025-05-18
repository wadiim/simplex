from simplex import *

import copy
import pytest


class TestSimplex:

    def test_get_pivot_pos_if_empty_tableau_then_returns_none(self):
        assert get_pivot_pos([[]]) == None


    def test_get_pivot_pos_if_single_row_then_returns_none(self):
        tableau = [
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_pivot_pos(tableau) == None


    def test_get_pivot_pos_if_no_neg_vals_in_bottom_row_then_returns_none(self):
        # NOTE: If there are no negative values in the objective function
        #       (bottom) row, that means, the optimal solution was already
        #       calculated.
        tableau = [
            [0, 1, 2, -1, 0, 8],
            [1, 0, -1, 1, 0 ,4],
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_pivot_pos(tableau) == None


    def test_get_pivot_pos_if_single_neg_val_in_bot_row_then_returns_valid_col_idx(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 1.5, 0, 8],
            [0, -10, 0, 20, 1, 320],
        ]

        assert get_pivot_pos(tableau)[1] == 1


    def test_get_pivot_pos_if_mul_neg_vals_in_bot_row_then_returns_idx_of_the_smallest(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [1, -30, -40, 0, 1, 0],
        ]

        assert get_pivot_pos(tableau)[1] == 2


    def test_get_pivot_pos_if_all_quotiens_are_ignored_then_returns_none(self):
        tableau = [
            [0, 0.5,  -1, -0.5, 0, 4], # negative quotient
            [1, 0.5,   0,  0.5, 0, 8], # zero in numerator
            [1, 0.5,   1,  0.5, 0, 0], # zero in denominator
            [1, -30, -40,    0, 1, 0],
        ]

        assert get_pivot_pos(tableau) == None


    def test_get_pivot_pos_if_valid_pivot_row_exists_then_returns_its_idx(self):
        tableau = [
            [1, 1, 1, 0, 0, 12], # 12/1 = 12
            [2, 1, 0, 1, 0, 16], # 16/2 = 8
            [-40, -30, 0, 0, 1],
        ]

        assert get_pivot_pos(tableau) == (1, 0)


    def test_perform_pivoting_if_already_solved_then_returns_unchanged_tableau(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [0, 10, 0, 20, 1, 320],
        ]

        tableau_copy = copy.deepcopy(tableau)

        perform_pivoting(tableau)
        assert tableau == tableau_copy


    def test_perform_pivoting_if_not_pivoted_then_returns_correct_result(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [0, -10, 0, 20, 1, 320],
        ]

        expected_tableau = [
            [0, 1, 2, -1, 0, 8],
            [1, 0, -1, 1, 0, 4],
            [0, 0, 20, 10, 1, 400],
        ]

        perform_pivoting(tableau)
        assert tableau == expected_tableau


    def test_perform_pivoting_if_neg_nums_in_pivot_col_then_returns_correct_result(self):
        tableau = [
            [0,   2, 1, -2,  0,   4],
            [1,  -2, 0, 0.5, 0,   8],
            [0, -10, 0, 20,  1, 320],
        ]

        expected_tableau = [
            [0, 1, 0.5, -1,   0,    2],
            [1, 0, 1,   -1.5, 0,   12],
            [0, 0, 5,   10,   1,  340],
        ]

        perform_pivoting(tableau)
        assert tableau == expected_tableau


    def test_get_solution_if_non_basic_col_then_returns_valid_solution(self):
        tableau = [
            [0, 5, 1, 2, 0, 18],
            [1, 0, 0, 1, 0, 8],
            [0, 4, 0, 3, 1, 24],
        ]

        assert get_solution(tableau) == ([8, 0], 24)


    def test_get_solution_if_minimization(self):
        tableau = [
            [0, 1,  2, -1, 0,   8],
            [1, 0, -1,  1, 0,   4],
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_solution(tableau, Mode.MINIMIZATION) == ([20, 10], 400)


    def test_get_solution_if_all_cols_are_basic_then_returns_valid_solution(self):
        tableau = [
            [0, 1, 2, -1, 0, 8],
            [1, 0, -1, 1, 0, 4],
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_solution(tableau) == ([4, 8], 400)


    def test_perform_simplex_when_feasible_and_bounded(self):
        # Problem I:
        tableau = [
            [-2, 1, 1, 0, 0, 2],
            [1, 2, 0, 1, 0, 8],
            [-3, -2, 0, 0, 1, 0],
        ]

        assert perform_simplex(tableau) == ([8, 0], 24)

        # Problem II:
        tableau = [
            [1, 1, 1, 0, 0, 12],
            [2, 1, 0, 1, 0, 16],
            [-40, -30, 0, 0, 1, 0],
        ]

        assert perform_simplex(tableau) == ([4, 8], 400)


    def test_perform_simplex_when_unbounded(self):
        tableau = [
            [ 1,   0, 1, 0, 0, 7], # x1      <= 7
            [ 1,  -1, 0, 1, 0, 8], # x1 - x2 <= 8
            [-5,  -4, 0, 0, 1, 0], # Z = 5x1 + 4x2
        ]

        assert perform_simplex(tableau) == ([float('inf'), float('inf')], float('inf'))


    def test_perform_simplex_when_minimization(self):
        tableau = [
            [  1,   1, 1, 0, 0, 12],
            [  2,   1, 0, 1, 0, 16],
            [-40, -30, 0, 0, 1,  0],
        ]

        assert perform_simplex(tableau, Mode.MINIMIZATION) == ([20, 10], 400)


    def test_to_tableau_if_var_count_equals_constraint_count(self):
        goal_function = [40.0, 30.0] # Z = 40x1 + 30x2
        constraints = [
            [1, 1, 12], # x1 + x2 <= 12
            [2, 1, 16], # 2x1 + x2 <= 16
        ]

        expected = [
            [1, 1, 1, 0, 0, 12],
            [2, 1, 0, 1, 0, 16],
            [-40, -30, 0, 0, 1, 0],
        ]

        assert to_tableau(goal_function, constraints) == expected


    def test_to_tableau_if_var_count_greater_than_constraint_count(self):
        goal_function = [40.0, 30.0, 20.0]
        constraints = [
            [1, 1, 3, 12],
            [2, 1, 0, 16],
        ]

        expected = [
            [  1,   1,   3, 1, 0, 0, 12],
            [  2,   1,   0, 0, 1, 0, 16],
            [-40, -30, -20, 0, 0, 1,  0],
        ]

        assert to_tableau(goal_function, constraints) == expected


    def test_to_tableau_if_var_count_less_than_constraint_count(self):
        goal_function = [40.0, 30.0]
        constraints = [
            [1, 1, 12],
            [2, 1, 16],
            [0, 2, 11],
        ]

        expected = [
            [  1,   1, 1, 0, 0, 0, 12],
            [  2,   1, 0, 1, 0, 0, 16],
            [  0,   2, 0, 0, 1, 0, 11],
            [-40, -30, 0, 0, 0, 1,  0],
        ]

        assert to_tableau(goal_function, constraints) == expected


    def test_to_tableau_if_minimization_mode(self):
        goal_function = [6.0, 4.0]
        constraints = [
            [-2, -1, -3],
            [ 1, -2,  2],
            [-3, -1,  0],
            [ 1, -2, -1],
        ]

        expected = [
            [ 2, -1, 3, -1, 1, 0, 0, 6],
            [ 1,  2, 1,  2, 0, 1, 0, 4],
            [-3,  2, 0, -1, 0, 0, 1, 0],
        ]

        assert to_tableau(goal_function, constraints, Mode.MINIMIZATION) == expected


    def test_to_basic_matrix(self):
        goal_function = [40.0, 30.0]
        constraints = [
            [1, 1, 12],
            [2, 1, 16],
            [0, 2, 11],
        ]

        expected = [
            [ 1,  1, 12],
            [ 2,  1, 16],
            [ 0,  2, 11],
            [40, 30,  0],
        ]

        assert to_basic_matrix(goal_function, constraints) == expected


    def test_transpose_basic_matrix(self):
        matrix = [
            [ 1,  1, 12],
            [ 2,  1, 16],
            [ 0,  2, 11],
            [40, 30,  0],
        ]

        expected = [
            [ 1,  2,  0, 40],
            [ 1,  1,  2, 30],
            [12, 16, 11,  0],
        ]

        assert transpose_basic_matrix(matrix) == expected


    def test_basic_matrix_to_tableau(self):
        matrix = [
            [ 1,  2,  0, 40],
            [ 1,  1,  2, 30],
            [12, 16, 11,  0],
        ]

        expected = [
            [  1,   2,   0, 1, 0, 0, 40],
            [  1,   1,   2, 0, 1, 0, 30],
            [-12, -16, -11, 0, 0, 1,  0],
        ]

        assert basic_matrix_to_tableau(matrix) == expected
