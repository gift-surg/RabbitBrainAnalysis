import os
import copy
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


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

    for l in labels_to_keep:
        out_data_mask = np.logical_or(out_data_mask, np.equal(in_data, l))

    return out_data_mask * in_data


def keep_only_one_label_path(input_im_path, output_im_path, labels_to_keep):

    # check parameters
    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_selected_labels = keep_only_one_label(data_labels,
                                               labels_to_keep=labels_to_keep)

    im_relabelled = set_new_data(im_labels, data_selected_labels)
    nib.save(im_relabelled, output_im_path)


''' Methods to get values below a label '''


def get_values_below_label(image, segmentation, label):
    np.testing.assert_array_equal(image.shape, segmentation.shape)
    below_label_places = segmentation == label
    return [i for i in (below_label_places * image).flatten() if i > 0.00000000001]


def get_intensities_statistics_matrix(warped, segmentation, percentile=10):
    """
    Given an image and a segmentation
    (or a stack of images and a stack of segmentations)
    provides a matrix M

                   | label 1  | label 2 | label 3 | ...
    ------------------------------------------------------------------------
    inf percentile |
    mean           |
    sup percentile |

    where M[0, k] is the superior quartile of the grayscale values below the label k
          M[1, k] is the mean of the grayscale values below label k
          M[0, k] is the inferior quartile of the grayscale values below the label k

    The size of the matrix is 3 x max label.
    If the segmentation has 2 labels 0 and 255, than the matrix has shape 3 x 255 and it is mostly composed by NAN,
    where the labels are not present in the segmentation.

    :param warped: image
    :param segmentation: segmentation
    :param percentile: percentile epsilon so that inf percentile = 0 + percentile , sup percentile = 100 - percentile
    :return: table M
    """
    np.testing.assert_array_equal(warped.shape, segmentation.shape)
    list_all_labels = list(set(segmentation.astype('uint64').flat))
    list_all_labels.sort().pop(0)

    if len(warped.shape) == 4:
        num_stacks = warped.shape[3]
        M = np.empty([3, list_all_labels[-1], num_stacks], dtype=np.float64)
        M.fill(np.NAN)
        for stack_id in range(num_stacks):
            for label in list_all_labels:

                vals = get_values_below_label(warped[..., stack_id], segmentation[..., stack_id], label)

                M[0, label, stack_id] = np.percentile(vals, 0 + percentile)
                M[1, label, stack_id] = np.mean(vals)
                M[2, label, stack_id] = np.percentile(vals, 100 - percentile)
    else:
        M = np.empty([3, len(list_all_labels)], dtype=np.float64)
        M.fill(np.NAN)
        for label in list_all_labels:

            vals = get_values_below_label(warped, segmentation, label)

            M[0, label] = np.percentile(vals, 25)
            M[1, label] = np.mean(vals)
            M[2, label] = np.percentile(vals, 75)

    return M
