"""
Measurements on labels.
"""
import numpy as np
import nibabel as nib


def volume_from_binary_segmentation_path(segmentation_path):
    """
    For the moment only one label.
    :param segmentation_path:
    :param label_to_measure: only one label for the moment.
    :param voxel:
    :return:
    """
    im = nib.load(segmentation_path)
    im_data = im.get_data()

    num_voxels = np.count_nonzero(im_data)
    mm_3 = num_voxels * np.abs(np.prod(np.diag(im.get_affine())))

    return num_voxels, mm_3
