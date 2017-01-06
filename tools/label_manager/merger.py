import os
import copy
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def merge_labels_from_4d(in_data):
    """
    Can be the inverse function of split label.
    From labels splitted in the 4d dimension, it reconstruct the
    original label volume from the masks in each time-point.
    The label index corresponds to the number of the slice (starting from 1).
    :param in_data: 4d volume
    :return:
    """
    msg = 'Input array must be 4-dimensional.'
    assert len(in_data.shape) == 4, msg

    in_data_shape = in_data.shape
    out_data = np.zeros(in_data_shape[:3], dtype=in_data.dtype)

    for i in xrange(in_data_shape[0]):
        for j in xrange(in_data_shape[1]):
            for k in xrange(in_data_shape[2]):

                # position of element 1 in the row (i,j,k,:)
                non_zero_label = list(np.where(np.in1d(in_data[i, j, k, :].ravel(), [3, 5]))[0])
                if len(non_zero_label) > 1:
                    print 'More than one label at one voxel:' \
                          'voxel = {0}, labels = {1}'.format([i, j, k], non_zero_label)

                out_data[i, j, k] = non_zero_label[0]

    return out_data


def merge_labels_from_4d_path(input_im_path, output_im_path):

    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')
    if not os.path.isfile(output_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_relabelled = merge_labels(data_labels)

    im_relabelled = set_new_data(im_labels, data_relabelled)
    nib.save(im_relabelled, output_im_path)



def label_merger(in_data, labels_to_merge, leading_label=None):
    """
    from an array of labels it merges (in the same dimension) the labels in the
    list to the new_label. If new_label is None then it takes as the new label
    the first of the list.
    If new_label is not None it must be one of the label in the list
    labels_to_merge or must not be in the image (safety reason).
    :param in_data: 2d 3d array of integers
    :param labels_to_merge: list of labels in im_data
    :param leading_label: value assigned to the merged labels. First of
    labels_to_merge if None
    :return: input array with selected labels merged in the new label or in the
    first label of the labels_to_merge
    lists.
    """

    list_labels = list(set(in_data.astype('uint64').flat))
    list_labels.sort()

    # sanity tests:
    

    # raise warning if labels to merge are not in the image:
    if new_label is not None:
        new_label = labels_to_merge[0]
    return 0


def label_merger_path(im_data_path, out_data_path, labels_to_merge,
                      new_label=None):
    pass
