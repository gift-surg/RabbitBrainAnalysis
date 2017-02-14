import numpy as np

from os.path import join as jph
from definitions import root_pilot_study
from tools.label_manager.symmetriser import sym_labels


root_data = jph(root_pilot_study, 'A_template_atlas_ex_vivo/1305')
pfi_anatomy = jph(root_data, 'all_modalities/1305_T1.nii.gz')
pfi_atlas = jph(root_data, 'segmentations/automatic/1305_manual_segmentationV2_half.nii.gz')
pfi_atlas_new = jph(root_data, 'segmentations/automatic/1305_manual_segmentationV2_half_SYM.nii.gz')


left = [5, 7, 9, 11, 13, 15, 17, 19, 21] + [25, 27, 31] + [43, 45, 47] + [53, 55, 69, 71, 75, 83, 109] + \
    [129, 133, 135, 139, 141, 179, 211, 219, 223, 225, 227, 229, 239, 241, 243, 247, 249, 251]

center = [77, 78, 121, 127, 151, 153, 161, 201, 213, 215, 218, 233, 237, 253]
right = [i + 1 for i in left]


print len(list(set(left+center+right)))

sym_labels(pfi_anatomy,
           pfi_atlas,
           labels_input=left + center,
           result_img_path=pfi_atlas_new,
           results_folder=jph(root_data, 'segmentations/automatic'),
           labels_transformed=right + center,
           coord='z')
