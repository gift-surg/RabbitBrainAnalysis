import numpy as np
import nibabel as nib
import os
from os.path import join as jph

from tools.auxiliary.utils import set_new_data


def manual_sort_MSME_path(im_input_path, im_output_path):
    """
    Remapping of the MSME T2 from paravision to a nifty format where
    (x,y,z,e) are the x,y,z, coordinates of the volume and e are the echo coordinates.

    The input files presents with 2 consecutive slices with echoes in the same z slice.

    As it is       | as we like it to be
    ----------------------------------
    (x,y,0:15,0)   | (x,y,00:15)
    (x,y,16:32,0)  | (x,y,1,0:15)
    (x,y,0:15,1)   | (x,y,2,0:15)
    (x,y,16:32,1)  | (x,y,3,0:15)
    (x,y,0:15,2)   | (x,y,4,0:15)
    (x,y,16:32,2)  | (x,y,5,0:15)
      ...            ...
    (x,y,0:15,t)   | (x,y,2*t,0:15)
    (x,y,16:32,t)  | (x,y,2*t+1,0:15)

    :param subj_path:
    :return:
    """
    im = nib.load(im_input_path)
    im_data = im.get_data()

    msg = 'method customised for a selected shape: recustomise the method according to the shape.'
    assert im_data.shape == (240, 240, 32, 16), msg

    new_data = np.zeros_like(im_data)

    for t in xrange(16):
        print t
        new_data[:, :, 2 * t, 0:16] = im_data[:, :, 0:16, t]
        new_data[:, :, 2 * t + 1, 0:16] = im_data[:, :, 16:32, t]

    im_new = set_new_data(im, new_data)

    nib.save(im_new, im_output_path)
    print 'image saved in ' + im_output_path


# load data:

subject_folder_path = '/Users/sebastiano/Desktop/test_manual_sort'
subject_input_name  = '1305_MSME.nii.gz'
subject_reshuffled_name  = '1305_MSME_reshuffled_test.nii.gz'
subject_reoriented_name  = '1305_MSME_proper.nii.gz'

# extract slices:

manual_sort_MSME_path(jph(subject_folder_path, subject_input_name), jph(subject_folder_path, subject_reshuffled_name))

# reorient reshuffled data:
cmd = 'cp {0} {1} ' \
      'fslorient -deleteorient {1}; ' \
      'fslswapdim {1} x z -y {1}; ' \
      'fslorient -setqformcode 1 {1}; '.format(jph(subject_folder_path, subject_reshuffled_name),
                                        jph(subject_folder_path, subject_reoriented_name))

os.system(cmd)
