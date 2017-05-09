# Draft code

"""
After manual processing and alignment: template creation with NiftyReg.

Conditional random field:
weighted approach based on
phase 1)
    mutual agreement (majority voting with variable doubt threshold)
     - some labels will be certain, some other will not.
phase 2)
    Closeness to a certain value (w1)
    Unrealistic image value (w2)  - The label is not above any voxel whose value in between the sigmas of the one below the certain values.
    goodness of the registration (LNCC, patch shape and values between warped and the target image).
"""

from os.path import join as jph

from definitions import root_pilot_study

source_subjects = ['1305', '1702', '1805']
target_subject = '2002'

pfo_segmentations = jph(root_pilot_study, 'A_template_atlas_ex_vivo', target_subject, 'segmentations')
pfo_intermediate  = jph(pfo_segmentations, 'z_groupwise_intermediate')
pfo_automatic     = jph(pfo_segmentations, 'automatic')
pfo_experiments   = jph(pfo_segmentations, 'zz_label_fusion_experiments')

pfi_target_T1 = jph(root_pilot_study, 'A_template_atlas_ex_vivo', target_subject, 'all_modalities',
                    target_subject + '_T1.nii.gz')

test_tag = '_test_1'

# import images as arrays

list_stack_seg = []
list_stack_warp = []

# Use the last version of niftyseg + label manager


