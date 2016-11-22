import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def filter_connected_components_by_volume(im_input, num_cc_to_filter=10):
    """
    Given a mask image (volex values are integers from 1 to something), it takes the num_cc_to_filter with maximal
    volume and it relabels them from 1 to num_cc_to_filter, where 1 is the component with the biggest volume.
    If components are connected then it will provides the first num_cc_to_filter connected components divided by
    volumes.
    :param im_input: mask
    :param num_cc_to_filter:
    :return:
    """

    im_data = im_input.get_data().astype(np.int32)


    new_data = np.zeros_like(im_data)

    volumes_per_label = [0,] * np.max(im_data)

    print np.max(im_data)

    dim_x, dim_y, dim_z = list(im_data.shape)

    for i in range(dim_x):
        for j in range(dim_y):
            for k in range(dim_z):
                if im_data[i, j, k] > 0:
                    volumes_per_label[im_data[i, j, k] - 1] += 1

    list_volumes_copy = volumes_per_label[:]
    max_volumes = []
    max_labels = []

    for m in range(num_cc_to_filter):
        max_value = max(list_volumes_copy)
        max_index = list_volumes_copy.index(max_value)

        max_volumes += [max_value]
        max_labels += [max_index + 1]

        list_volumes_copy[max_index] = 0
        print
        print m
        print list_volumes_copy

    for i in range(dim_x):
        for j in range(dim_y):
            for k in range(dim_z):
                if im_data[i, j, k] in max_labels:
                    new_data[i, j, k] = max_labels.index(im_data[i, j, k]) + 1

    im_output = set_new_data(im_input, new_data)
    return im_output


def filter_connected_components_by_volume_path(im_input_path, im_output_path, num_cc_to_filter=10):

    im_input = nib.load(im_input_path)
    im_output = filter_connected_components_by_volume(im_input, num_cc_to_filter=num_cc_to_filter)
    nib.save(im_output, im_output_path)