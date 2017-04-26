from definitions import root_pilot_study

from tools.auxiliary.utils import set_new_data

import os
from os.path import join as jph
import nibabel as nib
import numpy as np


def crop_no_z(pfi):

    if jph(os.path.basename(pfi)).startswith('z_'):

        pfi_new = jph(os.path.dirname(pfi), os.path.basename(pfi)[2:])
        print pfi_new
        im_histo = nib.load(pfi)
        new_data = im_histo.get_data()[:, :, 90:]
        new_im = set_new_data(image=im_histo, new_data=new_data)
        nib.save(new_im, pfi_new)


def crop(pfi, pfi_new):
    im_histo = nib.load(pfi)
    new_data = im_histo.get_data()[:, :, 90:]
    new_im = set_new_data(image=im_histo, new_data=new_data)
    nib.save(new_im, pfi_new)



pfi_old = '/Users/sebastiano/Dropbox/RabbitEncephalopathyofPrematurity-MRI/pilot_study/A_template_atlas_ex_vivo/1201/segmentations/manual/z_1201_manual_refinement_v1.nii.gz'
pfi_new = '/Users/sebastiano/Dropbox/RabbitEncephalopathyofPrematurity-MRI/pilot_study/A_template_atlas_ex_vivo/1201/segmentations/manual/1201_manual_refinement_v1.nii.gz'
crop(pfi_old, pfi_new)

#
# pfo_root_main = jph(root_pilot_study, 'A_template_atlas_ex_vivo')
#
# pfi_1305_in_histological_coordinates = jph('Utils', '1305_histological_orientation',
#                                              'z_1305_T1_histo.nii.gz')
# pfi_1305_in_histological_coordinates_FULL = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                              '1305_T1_histo_FULL.nii.gz')
#
# pfi_1305_in_histological_coordinates_roi_mask = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                                     '1305_T1_histo_roi_mask.nii.gz')
#
# pfi_1305_in_histological_coordinates_brain_mask = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                                     '1305_T1_histo_brain_mask.nii.gz')
#
#
# pfi_1305_in_histological_coordinates_new = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                              '1305_T1_histo_new.nii.gz')
#
# pfi_1305_in_histological_coordinates_FULL_new = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                              '1305_T1_histo_FULL_new.nii.gz')
#
# pfi_1305_in_histological_coordinates_roi_mask_new = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                                     '1305_T1_histo_roi_mask_new.nii.gz')
#
# pfi_1305_in_histological_coordinates_brain_mask_new = jph(pfo_root_main, 'Utils', '1305_histological_orientation',
#                                                     '1305_T1_histo_brain_mask_new.nii.gz')
#
# print crop_no_z(pfi_1305_in_histological_coordinates)