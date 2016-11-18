import numpy as np

from tools.parsers.parse_brukert_txt import matrix_per_list_of_arrays


def test_matrix_per_list_of_arrays():
    a = np.array([[2,0,0],[0,0,1],[0,0,2]])
    b = np.array(range(15)).reshape(5,3)
    expected_ans = np.array([  [ 0,  2,  4],
                               [ 6,  5, 10],
                               [12,  8, 16],
                               [18, 11, 22],
                               [24, 14, 28]])

    obtained_ans = matrix_per_list_of_arrays(a, b)
    np.testing.assert_array_equal(expected_ans,obtained_ans)


test_matrix_per_list_of_arrays()
