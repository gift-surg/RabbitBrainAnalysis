"""
2 structures involved in this code:

swap-labels structure: e.g.
a = [[1,2,3], [3,4,12]]
permutation structure: e.g.
a = [[1,2,3], [2,3,1]]
"""

import copy
import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def is_valid_permutation(in_perm):
    """
    A permutation is a list of 2 lists of same size:
    a = [[1,2,3], [2,3,1]]
    means permute 1 with 2, 2 with 3, 3 with 1.
    :param in_perm: input permutation
    :return : True/False if the permutation is valid
    """
    if not len(in_perm) == 2:
        return False
    if not len(in_perm[0]) == len(in_perm[1]):
        return False
    if not all(isinstance(n, int) for n in in_perm[0]):
        return False
    if not all(isinstance(n, int) for n in in_perm[1]):
        return False
    if not set(in_perm[0]) == set(in_perm[1]):
        return False
    return True


def permute_labels(in_data, permutation, is_permutation=True):
    """
    Permute the values of the labels in an int image.
    :param in_data:
    :param permutation:
    :param is_permutation: False if the labels are not not permuted in a permutation,
    e.g. perm = [[1,2,3], [3,4,12]] (swap-labels structure, not permutation)
    :return:
    """
    if is_permutation:
        assert is_valid_permutation(permutation), 'Input permutation not valid.'

    new_data = copy.deepcopy(in_data)

    for k in range(len(permutation[0])):
        places = in_data == permutation[0][k]
        np.place(new_data, places, permutation[1][k])

    return new_data


def permute_labels_path(pfi_in_image, permutation, pfi_out_image, is_permutation=True):
    # check parameters
    if not os.path.isfile(pfi_in_image):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(pfi_in_image)
    data_labels = im_labels.get_data()
    data_permuted = permute_labels(data_labels, permutation, is_permutation=is_permutation)

    im_relabelled = set_new_data(im_labels, data_permuted)
    nib.save(im_relabelled, pfi_out_image)


def get_permutation_form_label_descriptor(pfi_label_descriptor):
    f = open(pfi_label_descriptor, 'r')
    swap_labels = [[], []]
    index = 0
    for line in f:
        first_element = line.split()[0]
        if first_element.isdigit():
            if not index == int(first_element):
                swap_labels[0] += [index, ]
                swap_labels[1] += [int(first_element), ]
            index += 1

    f.close()

    return swap_labels


def remove_untouchable_from_swap_label(in_swap_labels, untouchable_labels):
    """
    removes the elements that should not be swapped from the swap_label structure.
    e.g.
    in_swap_labels = [[1,2,3,4], [3,4,12,13]]
    untouchable_labels = [12, 13]
    return [[1,2], [3,4]]
    :param in_swap_labels:
    :param untouchable_labels:
    :return:
    """
    out_swap_labels = copy.deepcopy(in_swap_labels)

    for j in in_swap_labels[1]:
        if j in untouchable_labels:
            pos_j = out_swap_labels[1].index(j)
            out_swap_labels[0].pop(pos_j)
            out_swap_labels[1].pop(pos_j)

    return out_swap_labels


def apply_permutation_to_label_descriptor(pfi_in_label_descriptor_input, in_permutation, pfi_out_label_descriptor):
    # TODO: test before using!
    # use something like '{message:{fill}{align}{width}}'.format(message='Hi', fill=' ', align='<', width=16)
    # to format the space filling!
    cmd = 'cp {0} {1}'.format(pfi_in_label_descriptor_input, pfi_out_label_descriptor)
    os.system(cmd)

    old = open(pfi_in_label_descriptor_input, 'r')
    new = open(pfi_out_label_descriptor, 'w')

    index = 0
    for line in old:

        first_element = line.split()[0]
        if first_element.isdigit():

            line_splitted = line.split()
            line_splitted[0] = str(index)

            new_line = '    '.join(line_splitted)
            new.write(new_line)

            index += 1
        else:
            new.write(line)

    old.close()
    new.close()


