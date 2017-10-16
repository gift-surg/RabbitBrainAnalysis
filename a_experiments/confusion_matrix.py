import os
from os.path import join as jph
import numpy as np
import pandas as pd
import seaborn as sn
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from labels_manager.main import LabelsManager as LM
from labels_manager.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager
from labels_manager.tools.caliber.distances import dice_score, dispersion, covariance_distance, hausdorff_distance


"""
Getting the confusion matrix produced by two segmentations.
"""

# auxiliaries:

def dice_score_specific_label(im_segm1, im_segm2, labels1, labels2):
    # TODO this will be a new method in labels_manager.caliber.dist
    # slow but readable, can be refactored later.
    if isinstance(labels1, int):
        place1 = im_segm1.get_data() == labels1
    elif isinstance(labels1, list):
        place1 = np.zeros_like(im_segm1.get_data(), dtype=np.bool)
        for lab1 in labels1:
            place1 += im_segm1.get_data() == lab1
    else:
        raise IOError
    if isinstance(labels2, int):
        place2 = im_segm2.get_data() == labels2
    elif isinstance(labels2, list):
        place2 = np.zeros_like(im_segm2.get_data(), dtype=np.bool)
        for lab2 in labels2:
            place2 += im_segm2.get_data() == lab2
    else:
        raise IOError
    if float(np.count_nonzero(place1) + np.count_nonzero(place2)) == 0:
        return 0
    else:
        return 2 * np.count_nonzero(place1 * place2) / float(np.count_nonzero(place1) + np.count_nonzero(place2))


def dice_confusion_matrix(pfi_segm_1, pfi_segm_2, pfi_lab_descriptor, list_labels_to_omit=None):

    im_segm_1 = nib.load(pfi_segm_1)
    im_segm_2 = nib.load(pfi_segm_2)

    ldm = LabelsDescriptorManager(pfi_lab_descriptor)
    multilabel_descriptor = ldm.get_multi_label_dict()

    keys = multilabel_descriptor.keys()
    if list_labels_to_omit is not None:
        for l in list_labels_to_omit:
            keys.remove(l)

    num_keys = len(keys)

    confusion_matrix = np.zeros([num_keys, num_keys], dtype=np.float64)

    for k1_id, k1 in enumerate(keys):
        for k2_id, k2 in enumerate(keys):
            confusion_matrix[k1_id, k2_id] = dice_score_specific_label(im_segm_1,
                                                                       im_segm_2,
                                                                       multilabel_descriptor[k1],
                                                                       multilabel_descriptor[k2])

            print(' {0: <30} | {1: <30} : {2}'.format(k1, k2, confusion_matrix[k1_id, k2_id]))

    print(confusion_matrix)
    df_cm = pd.DataFrame(confusion_matrix, index=keys, columns=keys)

    return df_cm


def show_confusion_matrix(input_dataframe, title_plt=None, pfi_where_to_save=None):

    if title_plt is None:
        title_plt = 1
    fig = plt.figure(title_plt, figsize=(12, 8), dpi=100)
    plt.clf()
    ax = fig.add_subplot(111)
    # print ax.get_position()

    # ax.set_aspect(1)
    res = ax.matshow(np.array(input_dataframe.values), cmap=plt.cm.jet)

    width, height = input_dataframe.values.shape

    cbaxes = fig.add_axes([0.74, 0.02, 0.02, 0.73])
    cb = plt.colorbar(res, cax=cbaxes)

    ax.grid(False)

    ax.set_xticks(range(width))
    ax.set_xticklabels(input_dataframe.index, rotation=90, fontsize='small')
    ax.set_yticks(range(height))
    ax.set_yticklabels(input_dataframe.index, rotation=0, fontsize='small')
    ax.set_position([0.1, 0.02, 0.73, 0.73])  # left bottom width height

    if pfi_where_to_save is not None:
        plt.savefig(pfi_where_to_save)
        print('Graph saved in {}'.format(pfi_where_to_save))
    plt.show()


if __name__ == '__main__':

    # paths:
    root_rabbit = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/'
    root_main_sj = jph(root_rabbit, 'test_re_test_segmentation', 'target1111')

    pfi_segm_manual_1 = jph(root_main_sj, 'segm', 'approved', 'target1111_approved_first.nii.gz')
    pfi_segm_manual_2 = jph(root_main_sj, 'segm', 'approved', 'target1111_approved_second.nii.gz')
    pfi_segm_automatic_MV = jph(root_main_sj, 'segm', 'automatic', 'target1111_T1_segm_MV_s.nii.gz')
    pfi_multi_labels_descriptor = jph(root_rabbit, 'study', 'A_internal_template', 'LabelsDescriptors',
                                      'labels_descriptor_v8.txt')
    pfo_where_to_save = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/test_re_test_segmentation/outcomes'
    pfi_result_manual1_manual2 = jph(pfo_where_to_save, 'confusion_matrix_manual1_manual_2.pickle')
    pfi_result_manual1_automaticMV = jph(pfo_where_to_save, 'confusion_matrix_manual1_automaticMV.pickle')
    pfi_result_manual2_automaticMV = jph(pfo_where_to_save, 'confusion_matrix_manual2_automaticMV.pickle')

    # Show all the labels in the multi-labels descriptor:

    ldm = LabelsDescriptorManager(pfi_multi_labels_descriptor)
    multilabel = ldm.get_multi_label_dict()
    for k in multilabel.keys():
        print(' {0: >30} : {1}'.format(k, multilabel[k]))

    ''' create confusion matrix to pandas dataframe: '''
    # ---- Manual 1, manual 2
    # df_cm = dice_confusion_matrix(pfi_segm_manual_1, pfi_segm_manual_2, pfi_multi_labels_descriptor)
    # print df_cm
    # df_cm.to_pickle(pfi_result_manual1_manual2)

    # ---- Manual 1, MV
    # df_cm = dice_confusion_matrix(pfi_segm_manual_1, pfi_segm_automatic_MV, pfi_multi_labels_descriptor)
    # print df_cm
    # df_cm.to_pickle(pfi_result_manual1_automaticMV)

    # ---- Manual 2, MV
    df_cm = dice_confusion_matrix(pfi_segm_manual_2, pfi_segm_automatic_MV, pfi_multi_labels_descriptor)
    print df_cm
    df_cm.to_pickle(pfi_result_manual2_automaticMV)

    ''' Load pandas dataframe if created and plot it: '''

    # ---- Manual 1, manual 2

    # df_cm_loaded = pd.read_pickle(pfi_result_manual1_manual2)
    # show_confusion_matrix(df_cm_loaded, title_plt= 'Confusion matrix manual1, manual2',
    #                       pfi_where_to_save=jph(pfo_where_to_save, 'confusion_matrix_manual1_manual2.png'))

    # ---- Manual 1, MV
    # df_cm_loaded = pd.read_pickle(pfi_result_manual1_automaticMV)
    # show_confusion_matrix(df_cm_loaded,  title_plt= 'Confusion matrix manual1, automatic MV',
    #                       pfi_where_to_save=jph(pfo_where_to_save, 'confusion_matrix_manual1_automaticMV.png'))

    # ---- Manual 2, MV
    df_cm_loaded = pd.read_pickle(pfi_result_manual2_automaticMV)
    show_confusion_matrix(df_cm_loaded, title_plt='Confusion matrix manual2, automatic MV',
                          pfi_where_to_save=jph(pfo_where_to_save, 'confusion_matrix_manual2_automaticMV.png'))
