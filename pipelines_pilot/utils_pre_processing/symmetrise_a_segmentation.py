import numpy as np

import os
from os.path import join as jph
from definitions import root_pilot_study
from tools.label_manager.symmetriser import sym_labels


root_data = jph(root_pilot_study, 'A_template_atlas_ex_vivo', '1805')
pfi_anatomy = jph(root_data, 'all_modalities', '1805_T1.nii.gz')
pfi_atlas = jph(root_data, 'segmentations', 'automatic', '1805_prop_segm_from_1702_v5_half.nii.gz')
pfi_atlas_new = jph(root_data, 'segmentations', 'automatic', '1805_prop_segm_from_1702_v5_SYM.nii.gz')


msg = 'Non valid path : '
if not os.path.isfile(pfi_anatomy):
    IOError(msg + pfi_anatomy)
if not os.path.isfile(pfi_atlas):
    IOError(msg + pfi_atlas)
if not os.path.isfile(pfi_atlas_new):
    IOError(msg + pfi_atlas_new)



# ex vivo labels
left = [5, 7, 9, 11, 13, 15, 17, 19, 21] + [25, 27, 31] + [43, 45, 47] + [53, 55, 69, 71, 75, 83, 109] + \
    [129, 133, 135, 139, 141, 179, 211, 219, 223, 225, 227, 229, 239, 241, 243, 247, 249, 251]

center = [77, 78, 121, 127, 151, 153, 161, 201, 213, 215, 218, 233, 237, 253]
right = [i + 1 for i in left]


sym_labels(pfi_anatomy,
           pfi_atlas,
           list_labels_input=left + center,
           list_labels_transformed=right + center,
           pfi_result_segmentation=pfi_atlas_new,
           pfo_results=jph(root_data, 'segmentations', 'automatic',),
           coord='z')
