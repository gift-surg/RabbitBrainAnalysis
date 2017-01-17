"""
MSME T2 have not been always provided in a 'readable' format.
Some preprocessing was required.
The 'unreadable' versions are not kept, and can be found on the cluster.
"""

import numpy as np
import nibabel as nib
import os
from os.path import join as jph

from tools.auxiliary.utils import set_new_data
from tools.auxiliary.squeezer import squeeze_image_from_path
from definitions import root_pilot_study


def manual_sort_MSME_path(im_input_path, im_output_path, kind='ex_vivo'):
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

    :param im_input_path: path image input.
    :param im_output_path: path image resliced.
    :return:
    """
    im = nib.load(im_input_path)
    im_data = im.get_data()

    if not im_data.shape == (240, 240, 32, 16):
        msg = 'method customised for a selected shape: recustomise the method according to the shape.'
        print im_data.shape

    new_data = np.zeros_like(im_data)

    if kind == 'ex_vivo':
        for t in xrange(16):
            print t
            new_data[:, :, 2 * t, 0:16] = im_data[:, :, 0:16, t]
            new_data[:, :, 2 * t + 1, 0:16] = im_data[:, :, 16:32, t]

    # Other kinds do not have the same reshuffling...!

    im_new = set_new_data(im, new_data)

    nib.save(im_new, im_output_path)
    print 'Slice MSME extracted and image saved in ' + im_output_path


####################
# Data processing: #
####################

ex_vivo_process = False
update_main_and_erase_intermediate_steps = True

#  ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
subjects_ex_vivo = ['1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']


if ex_vivo_process:

    kind = 'ex_vivo'

    for sj in subjects_ex_vivo:

        input_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                        sj + '_MSME_T2.nii.gz')

        reshuffled_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res.nii.gz')

        reshuffled_reoriented_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res_oriented.nii.gz')

        # squeeze image
        print('Squeezing for subject ' + sj)
        squeeze_image_from_path(input_pfi, input_pfi)

        # extract slices:
        print('Extracting slices for subject ' + sj)
        manual_sort_MSME_path(input_pfi, reshuffled_pfi, kind=kind)

        # reorient reshuffled data:
        cmd = 'cp {0} {1}; ' \
              'fslorient -deleteorient {1}; ' \
              'fslswapdim {1} x z -y {1}; ' \
              'fslorient -setqformcode 1 {1}; '.format(reshuffled_pfi, reshuffled_reoriented_pfi)

        print('Reorienting sliced images for subject ' + sj)
        os.system(cmd)

if update_main_and_erase_intermediate_steps:

    kind = 'ex_vivo'

    for sj in subjects_ex_vivo:

        input_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                        sj + '_MSME_T2.nii.gz')

        reshuffled_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res.nii.gz')

        reshuffled_reoriented_pfi = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res_oriented.nii.gz')
        # overwrite the unoriented data
        cmd1 = 'cp {0} {1}; '.format(reshuffled_reoriented_pfi, input_pfi)
        cmd2 = 'rm {0} & rm {1}'.format(reshuffled_reoriented_pfi, reshuffled_pfi)

        os.system(cmd1)
        os.system(cmd2)
