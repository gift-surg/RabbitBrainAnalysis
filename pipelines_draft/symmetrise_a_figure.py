import os
from os.path import join as jph
from tools.label_manager.symmetriser import sym_labels
from tools.label_manager.relabeller import relabeller_path

root_data = '/Users/sebastiano/Desktop/test_flipper'

# input
img_3d_pfi = os.path.join(root_data, '0802_t1.nii.gz')
img_half_mask_pfi = os.path.join(root_data, '0802_t1_intrac_vol_half.nii.gz')

coord = 'z'

all_left_labels = list(range(1, 50, 2)) + list(range(61, 70, 2)) + [77, 101, 103]
all_center_labels = list(range(51, 61)) + list(range(71, 77)) + [100, 110, 150]
all_right_labels = list(range(2, 51, 2)) + list(range(62, 71, 2)) + [78, 102, 104]
all_extra_labels = []

in_img_anatomy_path = jph(root_data, '1305_T1_Female_285_oriented.nii.gz')
in_img_labels_path = jph(root_data, 'barcelona_atlas_on_1305_170119_half.nii.gz')
labels_input = all_left_labels + all_center_labels
labels_transformed = all_right_labels + all_center_labels

result_img_path = jph(root_data, 'barcelona_atlas_on_1305_170119_SYM_1.nii.gz')
results_folder = root_data

print '\n'
print labels_input, len(labels_input)

print labels_transformed, len(labels_transformed)

'''
sym_labels(in_img_anatomy_path,
           in_img_labels_path,
           labels_input,
           result_img_path,
           results_folder,
           labels_transformed=labels_transformed,
           coord='z')
'''

# relabeller_path(result_img_path, jph(root_data, 'only_part.nii.gz'), [103, 53, 27, 28], [103, 53, 27, 28])