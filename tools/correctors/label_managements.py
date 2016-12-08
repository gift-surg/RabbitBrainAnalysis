import os
import copy
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def relabeller(data, list_old_labels, list_new_labels):
    """
    From an np.array of labels (int values in reasonably small number)
    and a list of current labels and new labels, substitute them with the
    new list of labels. In the given order (first old with first new, second old with second new...)!
    :param data:
    :param list_old_labels:
    :param list_new_labels:
    :return:
    """
    new_data = copy.deepcopy(data)

    # sanity check: old and new have the same number of elements
    if not len(list_old_labels) == len(list_new_labels):
        raise IOError('Labels list does not have the same length.')

    for k in range(len(list_new_labels)):
        places = new_data == list_old_labels[k]
        if np.any(places):
            np.place(new_data, places, list_new_labels[k])
            print 'Label {0} substituted with label {1}'.format(list_old_labels[k], list_new_labels[k])
        else:
            print 'Label {0} not present in the array'.format(list_old_labels[k])

    return new_data


def relabeller_path(input_im_path, output_im_path, list_old_labels, list_new_labels):

    # check parameters
    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')
    if not os.path.isfile(output_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_relabelled = relabeller(data_labels, list_old_labels=list_old_labels, list_new_labels=list_new_labels)

    im_relabelled = set_new_data(im_labels, data_relabelled)
    nib.save(im_relabelled, output_im_path)


def split_labels(in_data, remove_gaps=True):
    """
    Split labels of a 3d segmentation in a 4d segmentation,
    one label for each slice, reordered in ascending order.
    Masks are relabelled in ascending order, if remove gaps is True.
    or kept the same if remove_gaps is False. In the second case,
    the number of the 4d does not correspond to the label index.
    remove_gaps=False makes split_labels biiective with the function
    merge_labels.
    :param in_data: labels (only positive labels allowed).
    :param remove_gaps:
    :return:
    """
    in_data_shape = in_data.shape

    msg = 'Input array must be 3-dimensional.'
    assert len(in_data.shape) == 3, msg

    list_labels = list(set(in_data.flat))
    list_labels.sort()
    max_label = max(list_labels)

    out_data = np.zeros(list(in_data_shape) + [max_label], dtype=in_data.dtype)

    for i in xrange(in_data_shape[0]):
        for j in xrange(in_data_shape[1]):
            for k in xrange(in_data_shape[2]):
                l = in_data[i, j, k]
                if not l == 0:
                    out_data[i, j, k, int(l) - 1] = 1

    if remove_gaps:
        # remove the empty slices:
        complementary_labels = list(set(list_labels) - set(range(1, max_label + 1)))
        complementary_labels.sort()
        out_data = np.delete(out_data, complementary_labels, axis=3)

    return out_data


def split_labels_path(input_im_path, output_im_path, remove_gaps=True):

    # check parameters
    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')
    if not os.path.isfile(output_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_relabelled = split_labels(data_labels, remove_gaps=remove_gaps)

    im_relabelled = set_new_data(im_labels, data_relabelled)
    nib.save(im_relabelled, output_im_path)


def merge_labels(in_data):
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


def merge_labels_path(input_im_path, output_im_path):

    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')
    if not os.path.isfile(output_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_relabelled = merge_labels(data_labels)

    im_relabelled = set_new_data(im_labels, data_relabelled)
    nib.save(im_relabelled, output_im_path)


def keep_only_one_label(in_data, labels_to_keep):
    """
    From a segmentation keeps only the values in the list labels_to_keep.
    :param in_data: labels (only positive labels allowed).
    :param labels_to_keep: list of the labels that will be kept.
    :return:
    """
    in_data_shape = in_data.shape

    msg = 'Input array must be 3-dimensional.'
    assert len(in_data.shape) == 3, msg

    msg = 'labels_to_keep must be a list of labels'
    assert len(labels_to_keep) > 0, msg

    list_labels = list(set(in_data.flat))
    list_labels.sort()

    msg = 'labels_to_keep {} in not delineated in the image'
    for j in labels_to_keep:
        assert j in list_labels, msg.format(j)

    out_data_mask = np.zeros_like(in_data).astype(bool)

    # refactor with true false masks.

    for l in labels_to_keep:
        out_data_mask = np.logical_or(out_data_mask, np.equal(in_data, l))


    '''
    for i in xrange(in_data_shape[0]):
        for j in xrange(in_data_shape[1]):
            for k in xrange(in_data_shape[2]):
                if in_data[i, j, k] in labels_to_keep:
                    out_data[i, j, k] = in_data[i, j, k]
    '''

    return out_data_mask * in_data



def keep_only_one_label_path(input_im_path, output_im_path, labels_to_keep):

    # check parameters
    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_selected_labels = keep_only_one_label(data_labels, labels_to_keep=labels_to_keep)

    im_relabelled = set_new_data(im_labels, data_selected_labels)
    nib.save(im_relabelled, output_im_path)
