# Draft code

"""
OLD! see under A_template_atlas_ex_vivo
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

import os
from os.path import join as jph

from definitions import root_pilot_study
from tools.auxiliary.utils import set_new_data


# paths to segmentations:

source_subjects = ['1305', '1702', '1805', '1201']
target_subject = '1203'

pfo_segmentations = jph(root_pilot_study, 'A_template_atlas_ex_vivo', target_subject, 'segmentations')
pfo_experiments   = jph(pfo_segmentations, 'zz_lab_fusion')

pfi_stack_seg = jph(pfo_experiments, 'stack_seg.nii.gz')
pfi_stack_warp = jph(pfo_experiments, 'stack_warp.nii.gz')
pfi_target  = jph(pfo_experiments, 'target.nii.gz')

# Majority voting:
pfi_output_MV = jph(pfo_experiments, 'output_MV.nii.gz')
cmd_mv = 'seg_LabFusion -in {0} -out {1} -MV'.format(pfi_stack_seg, pfi_output_MV)
print cmd_mv
os.system(cmd_mv)


# STAPLE:
pfi_output_STAPLE = jph(pfo_experiments, 'output_STAPLE.nii.gz')
cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1} '.format(pfi_stack_seg, pfi_output_STAPLE)
print cmd_staple
os.system(cmd_staple)

# STEPS:
pfi_output_STEPS = jph(pfo_experiments, 'fusion_STEPS_3_3_beta4p0_prop_update.nii.gz')
cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -MRF_beta {6} -prop_update'.format(pfi_stack_seg, pfi_output_STEPS,
                                                                             str(3),
                                                                             str(3),
                                                                             pfi_target,
                                                                             pfi_stack_warp, str(4.0))
print cmd_steps
os.system(cmd_steps)



'''


pfi_target_T1 = jph(root_pilot_study, 'A_template_atlas_ex_vivo', target_subject, 'all_modalities',
                    target_subject + '_T1.nii.gz')

test_tag = '_test_1'

# import images as arrays

list_stack_seg = []
list_stack_warp = []

for sj in source_subjects:

    pfi_seg = jph(pfo_automatic, sj + 'on' + target_subject + '_atlas_propagated' + test_tag + '.nii.gz')
    im_seg = nib.load(pfi_seg)
    list_stack_seg.append(im_seg.get_data()[:])

    pfi_warp = jph(pfo_intermediate, sj + 'on' + target_subject + '_bfc_res.nii.gz')
    im_warp = nib.load(pfi_warp)
    list_stack_warp.append(np.nan_to_num(im_warp.get_data().astype(np.float64)))

# create stack segmentation and warped
stack_seg = np.stack(list_stack_seg, axis=3)
stack_warp = np.stack(list_stack_warp, axis=3)

# create stack weight
im_T1 = nib.load(pfi_target_T1)

target = im_T1.get_data()


im_final_seg = set_new_data(im_seg, final_seg)
nib.save(im_final_seg, jph(pfo_experiments, 'FINAL_SEG.nii.gz'))
'''


'''
list_stack_seg.append(254 * np.ones_like(im_T1.get_data()))
# stack_weights = np.zeros(list(im_T1.shape) + [len(source_subjects) + 1], dtype=np.float64)

# create output mid-algorithm:
im_stack_seg = set_new_data(im_T1, stack_seg, new_dtype=np.int16)
im_stack_warp = set_new_data(im_T1, stack_warp)
# im_stack_weights = set_new_data(im_T1, stack_weights)

# create stack weights of the first step:

# stack_weights = phase_1_majority_voting(im_stack_seg.get_data())
#
# im_stack_weights = set_new_data(im_T1, stack_weights)
# nib.save(im_stack_weights, jph(pfo_experiments, 'stack_we.nii.gz'))

# load stack weights phase 1 if created before

im_stack_weights = nib.load(jph(pfo_experiments, 'stack_we.nii.gz'))


# create uncertain values mask
#
# uncertain_mask = get_uncertain_values_mask(im_stack_weights.get_data())
#
# im_uncertain_mask = set_new_data(im_T1, uncertain_mask)
# nib.save(im_uncertain_mask, jph(pfo_experiments, 'uncertain_mask_we.nii.gz'))

# load if uncertain values mask is created before
im_uncertain_mask = nib.load(jph(pfo_experiments, 'uncertain_mask_we.nii.gz'))



# intermediate: save uncertainty values region.


# save as temp
#
# nib.save(im_stack_seg, jph(pfo_experiments, 'stack_seg.nii.gz'))
# nib.save(im_stack_warp, jph(pfo_experiments, 'stack_warp.nii.gz'))


'''

