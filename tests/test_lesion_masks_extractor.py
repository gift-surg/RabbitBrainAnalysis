import numpy as np
import os
import nibabel as nib

from definitions import root_dir
from numpy.testing import assert_array_almost_equal
import matplotlib.pyplot as plt

from nose.tools import assert_equals, assert_raises, assert_almost_equals
from numpy.testing import assert_array_equal, assert_almost_equal


from tools.auxiliary.connected_components import filter_connected_components_by_volume


def test_lesion_masks_extractor_for_simple_input():
    """
    test on a cubic element if the connected components extractor works
    :return:
    """
    cmd = 'mkdir -p {0}'.format(os.path.join(root_dir, 'output'))
    os.system(cmd)

    dims = [105, 20, 20]

    im_data = np.zeros([dims[1], dims[2], 1])
    intervals = [50, 10, 50, 20, 25]
    weights   = [12, 2, 3, 4, 5]

    for i in range(len(intervals)):
        slice = weights[i] * np.ones([dims[1], dims[2], intervals[i]])
        im_data = np.concatenate((im_data, slice), axis=2)

    im = nib.Nifti1Image(im_data, np.eye(4))
    #nib.save(im, 'output/test.nii.gz')
    #os.system('open {}'.format('output/test.nii.gz'))

    #
    im_filtered = filter_connected_components_by_volume(im, num_cc_to_filter=3)

    # for the moment visual assessment test!
    nib.save(im_filtered, 'output/test_fil.nii.gz')
    os.system('open {}'.format('output/test_fil.nii.gz'))

    #cmd = 'rm -r {0}'.format(os.path.join(root_dir, 'output'))
    #os.system(cmd)


test_lesion_masks_extractor_for_simple_input()