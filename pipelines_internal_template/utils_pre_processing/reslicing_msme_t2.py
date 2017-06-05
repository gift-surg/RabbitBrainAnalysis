"""
MSME T2 have not been always provided in a 'readable' format.
Some preprocessing was required.
The 'unreadable' versions are not kept in the original folder, but can be found on the cluster.

First conversion from analyze to nifty happened with mrview.
Second conversion to reshuffle the slices in the correct order is done in

---
DEPRECATED AFTER CONVERTER!
"""

import numpy as np
import nibabel as nib
import os
from os.path import join as jph

from tools.auxiliary.utils import set_new_data
from tools.auxiliary.squeezer import squeeze_image_from_path
from definitions import root_pilot_study
from tools.correctors.MSME_T2_correctors import corrector_MSME_T2_path


####################
# Data processing: #
####################

ex_vivo_process = False
update_main_and_erase_intermediate_steps_ex_vivo = False
in_vivo_process = True


subjects_ex_vivo = ['1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
subjects_in_vivo = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']


if ex_vivo_process:

    kind = 'ex_vivo'

    for sj in subjects_ex_vivo:

        pfi_input = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                        sj + '_MSME_T2.nii.gz')

        pfi_reshuffled = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res.nii.gz')

        pfi_reshuffled_reoriented = jph(root_pilot_study, '0_original_data', kind, sj, 'MSME_T2',
                             'z_' + sj + '_MSME_T2_res_oriented.nii.gz')

        # squeeze image
        print('Squeezing for subject ' + sj)
        squeeze_image_from_path(pfi_input, pfi_input)

        # extract slices:
        print('Extracting slices for subject ' + sj)
        corrector_MSME_T2_path(pfi_input, pfi_reshuffled, modality=kind)

        # reorient reshuffled data:
        cmd = 'cp {0} {1}; ' \
              'fslorient -deleteorient {1}; ' \
              'fslswapdim {1} x z -y {1}; ' \
              'fslorient -setqformcode 1 {1}; '.format(pfi_reshuffled, pfi_reshuffled_reoriented)

        print('Reorienting sliced images for subject ' + sj)
        os.system(cmd)

if update_main_and_erase_intermediate_steps_ex_vivo:

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


if in_vivo_process:

    kind = 'ex_vivo'