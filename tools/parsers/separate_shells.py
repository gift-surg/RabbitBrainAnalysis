import numpy as np
import os
import nibabel as nib

from tools.auxiliary.utils import set_new_data, eliminates_consecutive_duplicates


def separate_shells_txt(b_vals, b_vects, num_initial_dir_to_skip=7, num_shells=3):
    """

    :param b_vals: input b-values
    :param b_vects: input b-vectors
    :param num_initial_dir_to_skip: Non all the initial values of the b-vals b-vects are useful. Where to start?
    :param num_shells:
    :return [[bvals splitted], [bvect splitted]]:
     a different list for each shell for b-vals and b-vect
    """
    b_vals = b_vals[num_initial_dir_to_skip:]
    b_vects = b_vects[num_initial_dir_to_skip:]

    b_vals_per_shell = []
    b_vect_per_shell = []

    for k in range(num_shells):
        b_vals_per_shell.append(b_vals[k::num_shells])
        b_vect_per_shell.append(b_vects[k::num_shells])

    # sanity check
    num_directions = len(b_vals_per_shell[0])
    for k in range(num_shells):
        if not len(b_vals_per_shell[k]) == len(b_vect_per_shell[k]) == num_directions:
            raise IOError

    return [b_vals_per_shell, b_vect_per_shell]


def separate_shells_txt_path(b_vals_path, b_vects_paths, output_folder, prefix='',
                             num_initial_dir_to_skip=7, num_shells=3):
    """

    :param b_vals_path:
    :param b_vects_paths:
    :param output_folder: folder where to save the parameters.
    :param prefix : prefix for the file as the subject tag. Empty string by default.
    :param num_initial_dir_to_skip:
    :param num_shells:
    :return:
    """

    b_vals = np.loadtxt(b_vects_paths)
    b_vects = np.loadtxt(b_vects_paths)

    [list_b_vals, list_b_vects] = separate_shells_txt(b_vals,
                                                      b_vects,
                                                      num_initial_dir_to_skip=num_initial_dir_to_skip,
                                                      num_shells=num_shells)

    # save here the bvals and bvects in separate lists.
    for i in range(num_shells):
        path_b_vals_shell_i = os.path.join(output_folder, prefix + '_DwEffBval.txt')
        path_b_vect_shell_i = os.path.join(output_folder, prefix + '_DwGradVec.txt')

        np.savetxt(path_b_vals_shell_i, list_b_vals[i])
        print 'B-values for shell {0} saved in {1}'.format(str(i), path_b_vect_shell_i)

        np.savetxt(path_b_vect_shell_i, list_b_vects[i])
        print 'B-vectors for shell {0} saved in {1}'.format(str(i), path_b_vals_shell_i)


def separate_shells_dwi(nib_dwi, num_initial_dir_to_skip=7, num_shells=3):
    pass


def separate_shells_dwi_path():
    pass