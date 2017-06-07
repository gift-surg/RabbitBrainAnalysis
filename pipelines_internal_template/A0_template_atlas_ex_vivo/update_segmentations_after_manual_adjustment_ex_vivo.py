"""
Generate preliminary results from subject 1305.
"""

import os

from tools.definitions import root_pilot_study
from labels_manager.tools.manipulations.symmetrizer import sym_labels
from tools.auxiliary.utils import print_and_run
# Path manager:

sj = '1305'
path_subject_folder = os.path.join(root_pilot_study, 'A_template_atlas_ex_vivo', sj)

# steps manager
step_symmetrise = False
step_first_cropping = False
step_smoothing = False
step_second_cropping = False
final_cleaning = True

######################################
# Symmetrise the manual segmentation #
######################################


path_template = os.path.join(path_subject_folder, 'all_modalities', '1305_T1.nii.gz')
path_half_atlas = os.path.join(path_subject_folder, 'segmentations', 'manually_corrected',
                               '1305_manual_adjustment_v1_half.nii.gz')
path_results_folder = os.path.join(path_subject_folder, 'segmentations', 'processed_from_manually_corrected')

path_result_sym = os.path.join(path_results_folder, 'y_1305_sym_segmentation.nii.gz')

if step_symmetrise:

    all_left_labels = list(range(1, 50, 2)) + list(range(61, 68, 2)) + [99, 101]
    all_center_labels = list(range(51, 61)) + [71, 72, 73, 74, 103, 105, 106]
    all_right_labels = list(range(2, 51, 2)) + list(range(62, 69, 2)) + [100, 102]
    all_extra_labels = [99, ]

    print 'Symmetrise one side of the segmentation on the other.'

    sym_labels(pfi_anatomy=path_template,
               pfi_segmentation=path_half_atlas,
               pfo_results=path_results_folder,
               pfi_result_segmentation=path_result_sym,
               list_labels_input=all_left_labels+all_center_labels,
               list_labels_transformed=all_right_labels+all_center_labels,
               reuse_registration=False,
               coord='z')

############################
# Crop with the brain mask #
############################

path_cropping_mask = os.path.join(root_pilot_study, 'A_template_atlas_ex_vivo', 'Utils', 'brain_mask',
                                  '1305_brain_mask.nii.gz')

path_result_cropped = os.path.join(path_results_folder, 'y_1305_segmentation_cropped.nii.gz')

if step_first_cropping:
    print 'Cropping the symmetrised segmentation with the brain maks.'
    cmd = 'seg_maths {0} -mul {1} {2} '.format(path_result_sym, path_cropping_mask, path_result_cropped)
    print_and_run(cmd)

#####################
# Initial smoothing #
#####################

path_final_result = os.path.join(path_results_folder, '1305_symetrised_segmentation.nii.gz')

if step_smoothing:
    print 'Perform an initial smoothing.'
    cmd = 'seg_maths {0} -smol 0.7 {1} '.format(path_result_cropped, path_final_result)
    print_and_run(cmd)


##############################
# Crop with brain mask again #
##############################

if step_second_cropping:
    print 'Crop again.'
    cmd = 'seg_maths {0} -mul {1} {2} '.format(path_final_result, path_final_result)
    print_and_run(cmd)

############
# Cleaning #
############

if final_cleaning:
    cmd = 'rm {0}/z_* & rm {0}/y_*'.format(path_results_folder)
    print_and_run(cmd)
