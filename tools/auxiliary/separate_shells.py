import numpy as np
import os
import nibabel as nib
from sympy.core.cache import clear_cache

from nilabels.tools.aux_methods.utils_nib import set_new_data


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


def separate_shells_txt_path(b_vals_path, b_vects_paths, output_folder=None, prefix='',
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
    if output_folder is None:
        output_folder = os.path.dirname(b_vals_path)

    b_vals = np.loadtxt(b_vals_path)
    b_vects = np.loadtxt(b_vects_paths)

    [list_b_vals, list_b_vects] = separate_shells_txt(b_vals,
                                                      b_vects,
                                                      num_initial_dir_to_skip=num_initial_dir_to_skip,
                                                      num_shells=num_shells)

    # save here the bvals and bvects in separate lists.
    for i in range(num_shells):
        path_b_vals_shell_i = os.path.join(output_folder, prefix + '_DwEffBval_shell' + str(i) + '.txt')
        path_b_vect_shell_i = os.path.join(output_folder, prefix + '_DwGradVec_shell' + str(i) + '.txt')

        np.savetxt(path_b_vals_shell_i, list_b_vals[i])
        print 'B-values for shell {0} saved in {1}'.format(str(i), path_b_vect_shell_i)

        np.savetxt(path_b_vect_shell_i, list_b_vects[i])
        print 'B-vectors for shell {0} saved in {1}'.format(str(i), path_b_vals_shell_i)


def separate_shells_dwi(nib_dwi, num_initial_dir_to_skip=7, num_shells=3):
    """
    Return a list of num_shell nibabel images, one image per shell.
    :param nib_dwi:
    :param num_initial_dir_to_skip:
    :param num_shells:
    :return:
    """
    im_data = nib_dwi.get_data()[..., num_initial_dir_to_skip:]

    list_nib_dwi_per_shells = []

    for i in range(num_shells):
        slice_i_data = im_data[..., i::num_shells]
        im_slice_i = set_new_data(nib_dwi, slice_i_data)
        list_nib_dwi_per_shells.append(im_slice_i)

        clear_cache()

    return list_nib_dwi_per_shells


def separate_shells_dwi_path(nib_dwi_path, output_folder=None, prefix='', suffix='_DWI_shell_',
                             num_initial_dir_to_skip=7, num_shells=3):

    if output_folder is None:
        output_folder = os.path.dirname(nib_dwi_path)

    im = nib.load(nib_dwi_path)

    list_nib_sliced = separate_shells_dwi(im, num_initial_dir_to_skip=num_initial_dir_to_skip, num_shells=num_shells)

    for i in range(num_shells):
        path_dwi_shell_i = os.path.join(output_folder, prefix + suffix + str(i) + '.nii.gz')
        nib.save(list_nib_sliced[i], path_dwi_shell_i)
        print 'B-values for shell {0} saved in {1}'.format(str(i), path_dwi_shell_i)
