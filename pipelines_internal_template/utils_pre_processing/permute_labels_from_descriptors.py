import os
from os.path import join as jph

from tools.label_manager.permute_labels import permute_labels_path, get_permutation_form_label_descriptor, \
    apply_permutation_to_label_descriptor, remove_untouchable_from_swap_label


root = '/Users/sebastiano/Desktop/test_labels_permutation'

pfi_input_segmentation = jph(root, 'segmentation_1305.nii.gz')
pfi_input_desciptor = jph(root, 'labels_corresp.txt')
# input descriptor is the descriptor with a modified order of the labels.

pfi_output_image = jph(root, 'segmentation_1305_new.nii.gz')
pfi_output_descriptor = jph(root, 'labels_corresp_new.txt')

# collect permutation from descriptor
perm = get_permutation_form_label_descriptor(pfi_input_desciptor)

print perm

perm = remove_untouchable_from_swap_label(perm, [255,])

print perm

perm = [perm[1], perm[0]]

print perm

# apply permutation to the image
permute_labels_path(pfi_input_segmentation, perm, pfi_output_image, is_permutation=False)

# apply permutation to the descriptor
#apply_permutation_to_label_descriptor()


