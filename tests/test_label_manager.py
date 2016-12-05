import numpy as np
import os
import nibabel as nib

from definitions import root_dir
from numpy.testing import assert_array_almost_equal
import matplotlib.pyplot as plt

from nose.tools import assert_equals, assert_raises, assert_almost_equals
from numpy.testing import assert_array_equal, assert_almost_equal
from tools.correctors.label_managements import relabeller


def test_label_manager_simple_input_simple_input():
    """
    test on a cubic element if the connected components extractor works
    :return:
    """
    cmd = 'mkdir -p {0}'.format(os.path.join(root_dir, 'output'))
    os.system(cmd)

    dims = [105, 20, 20]

    im_data = np.zeros([dims[1], dims[2], 1])
    intervals = [50, 10, 50, 20, 25]
    labels   = [1, 2, 3, 4, 5]

    for i in range(len(intervals)):
        # build the matrix we need
        single_slice = labels[i] * np.ones([dims[1], dims[2], intervals[i]])
        im_data = np.concatenate((im_data, single_slice), axis=2)

    # Apply relabeller
    im_data_renewed = relabeller(im_data, [1, 2, 3, 4, 5], [10, 20, 30, 40, 50])

    im_original = nib.Nifti1Image(im_data, np.eye(4))
    im_renewed = nib.Nifti1Image(im_data_renewed, np.eye(4))

    # for the moment visual assessment test!
    nib.save(im_original, os.path.join(root_dir, 'output/test_im1.nii.gz'))
    nib.save(im_renewed, os.path.join(root_dir, 'output/test_im2.nii.gz'))

    os.system('itksnap -g {}'.format(os.path.join(root_dir, 'output/test_im1.nii.gz')))
    os.system('itksnap -g {}'.format(os.path.join(root_dir, 'output/test_im2.nii.gz')))


test_label_manager_simple_input_simple_input()
