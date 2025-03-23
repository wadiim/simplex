from simplex import *

import copy
import pytest


class TestSimplex:

    def test_get_pivot_col_idx_if_empty_tableau_then_returns_neg_one(self):
        assert get_pivot_col_idx([[]]) == -1


    def test_get_pivot_col_idx_if_single_row_then_returns_neg_one(self):
        tableau = [
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_pivot_col_idx(tableau) == -1


    def test_get_pivot_col_idx_if_no_neg_vals_in_bottom_row_then_returns_neg_one(self):
        # NOTE: If there are no negative values in the objective function
        #       (bottom) row, that means, the optimal solution was already
        #       calculated.
        tableau = [
            [0, 1, 2, -1, 0, 8],
            [1, 0, -1, 1, 0 ,4],
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_pivot_col_idx(tableau) == -1


    def test_get_pivot_col_idx_if_single_neg_val_then_returns_valid_idx(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 1.5, 0, 8],
            [0, -10, 0, 20, 1, 320],
        ]

        assert get_pivot_col_idx(tableau) == 1


    def test_get_pivot_col_idx_if_mul_neg_vals_then_returns_idx_of_the_smallest_one(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [1, -30, -40, 0, 1, 0],
        ]

        assert get_pivot_col_idx(tableau) == 2


    def test_get_pivot_row_idx_if_empty_tableau_then_returns_neg_one(self):
        assert get_pivot_row_idx([[]], 0) == -1


    def test_get_pivot_row_idx_if_pivot_col_idx_invalid_then_throws_exception(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [1, -30, -40, 0, 1, 0],
        ]

        with pytest.raises(InvalidPivotColumnIndex):
            get_pivot_row_idx(tableau, 8)


    def test_get_pivot_row_idx_if_all_quotiens_are_ignored_then_returns_neg_one(self):
        tableau = [
            [0, 0.5,  -1, -0.5, 0, 4], # negative quotient
            [1, 0.5,   0,  0.5, 0, 8], # zero in numerator
            [1, 0.5,   1,  0.5, 0, 0], # zero in denominator
            [1, -30, -40,    0, 1, 0],
        ]

        assert get_pivot_row_idx(tableau, 2) == -1


    def test_get_pivot_row_idx_if_valid_pivot_row_exists_then_returns_its_idx(self):
        tableau = [
            [1, 1, 1, 0, 0, 12], # 12/1 = 12
            [2, 1, 0, 1, 0, 16], # 16/2 = 8
            [-40, -30, 0, 0, 1],
        ]

        assert get_pivot_row_idx(tableau, 0) == 1


    def test_perform_pivoting_if_invalid_pivot_row_idx_then_throws_exception(self):
        tableau = [
            [1, 1, 1, 0, 0, 12],
            [2, 1, 0, 1, 0, 16],
            [-40, -30, 0, 0, 1],
        ]

        with pytest.raises(InvalidPivotRowIndex):
            perform_pivoting(tableau, 42, 0)


    def test_perform_pivoting_if_invalid_pivot_col_idx_then_throws_exception(self):
        tableau = [
            [1, 1, 1, 0, 0, 12],
            [2, 1, 0, 1, 0, 16],
            [-40, -30, 0, 0, 1],
        ]

        with pytest.raises(InvalidPivotColumnIndex):
            perform_pivoting(tableau, 1, 42)


    def test_perform_pivoting_if_already_pivoted_then_returns_unchanged_tableau(self):
        tableau = [
            [0, 0.5, 1, -0.5, 0, 4],
            [1, 0.5, 0, 0.5, 0, 8],
            [0, -10, 0, 20, 1, 320],
        ]

        tableau_copy = copy.deepcopy(tableau)

        perform_pivoting(tableau, 1, 0)
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

        perform_pivoting(tableau, 0, 1)
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

        perform_pivoting(tableau, 0, 1)
        assert tableau == expected_tableau


    def test_get_solution_if_non_basic_col_then_returns_valid_solution(self):
        tableau = [
            [0, 5, 1, 2, 0, 18],
            [1, 0, 0, 1, 0, 8],
            [0, 4, 0, 3, 1, 24],
        ]

        assert get_solution(tableau) == ([8, 0], 24)


    def test_get_solution_if_all_cols_are_basic_then_returns_valid_solution(self):
        tableau = [
            [0, 1, 2, -1, 0, 8],
            [1, 0, -1, 1, 0, 4],
            [0, 0, 20, 10, 1, 400],
        ]

        assert get_solution(tableau) == ([4, 8], 400)


    def test_perform_simplex(self):
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
