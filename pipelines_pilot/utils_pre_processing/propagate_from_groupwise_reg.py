'''
Idea is to use the groupwise approach to propagate the segmentation:
Some anatomies have manual segmentation, some does not.
All the anatomies are averaged.
The manual segmentations are propagated in the middle space.
The manual segmentations are averaged.
The average manual seg is propagated back to the subjects that initially
does not have any manual segmentation.
This approach is in some sense robust to noise, but requires at least three
initial segmentations, to create a reasonable average segmentation.

'''
import numpy as np
import os
from os.path import join as jph

from tools.auxiliary.utils import print_and_run


# path manager:
root_folder = '/Users/sebastiano/Desktop'
pfo_groupwise_reg_results_subfolders_structure = jph(root_folder, 'z_test_average', 'results')
pfo_input_segmentation = jph(root_folder, 'z_test_average', 'input_segmentations')
pfo_input_propagation = jph(root_folder, 'z_test_average', 'output_propagations')

num_iterations = 10
subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
subjects = ['1305', '1702']

list_pfi_segmentations_to_propagate = [jph(, sj + 'propagate_me.nii.gz') for sj in subjects]

list_pfi_mask

# path sanity check:
# TODO in progress


# Step manager
safety_on = True
steps_map = {'Affine resampling' : True,
             'Nrig resampling'   : True}

for it xrange(num_iterations):

    if steps_map['Affine resampling']:

        cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
                 pfi_destination_subject, pfi_starting_atlas, pfi_affine_transf, pfi_atlas_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Nrig resampling']:
