import os
import copy
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def relabeller(data, list_old_labels, list_new_labels):
    """
    From an np.array of labels (int values in reasonably small number)
    and a list of current labels and new labels, substitute them with the
    new list of labels. In the given order (first old with first new, second
    old with second new...)!
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


def relabeller_path(input_im_path, output_im_path, list_old_labels, list_new_labels, new_dtype=None):

    # check parameters
    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_relabelled = relabeller(data_labels, list_old_labels=list_old_labels, list_new_labels=list_new_labels)

    im_relabelled = set_new_data(im_labels, data_relabelled, new_dtype=new_dtype)
    nib.save(im_relabelled, output_im_path)


def label_permutator():
    """
    Permute the values of the labels in an int image.
    """
    # prima splitta in una 4D. Poi cambia le etichette separatamente dove vanno
    # cambiate. infine ripacchetta la fingura.
    # TODO


def assign_all_other_labels_the_same_value(data_in, labels_to_keep, same_value_label=255):
    """
    All the labels that are not in the list labels_to_keep will be given the value same_value_label
    :param im_data:
    :param labels_to_keep:
    :param same_value_label:
    :return:
    """

    list_labels = list(set(data_in.astype('uint64').flat))
    list_labels.sort()

    labels_that_will_have_the_same_value = list(set(list_labels) - set(labels_to_keep) - {0})

    places = np.zeros_like(data_in).astype(bool)
    new_data = copy.deepcopy(data_in)

    for k in labels_that_will_have_the_same_value:
        places += new_data == k

    np.place(new_data, places, same_value_label)

    return new_data