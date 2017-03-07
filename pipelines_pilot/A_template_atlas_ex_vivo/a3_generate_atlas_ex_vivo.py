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

import os
from os.path import join as jph
import copy
import numpy as np
import nibabel as nib
from collections import Counter

from definitions import root_pilot_study
from tools.auxiliary.utils import set_new_data


# utils:


def phase_1_majority_voting(stack_segmentations, threshold=2):
    # input is a numpy array
    sh = list(stack_segmentations.shape)
    sh[-1] += 1
    stack_weights = np.zeros(sh, dtype=np.float64)
    for x in xrange(stack_segmentations.shape[0]):
        for y in xrange(stack_segmentations.shape[1]):
            for z in xrange(stack_segmentations.shape[2]):
                c = Counter(list(stack_segmentations[x, y, z, :]))
                if c.most_common(1)[0][1] >= threshold:  # number of occurrences of the most common is >= threshold
                    first_majority_index = list(stack_segmentations[x, y, z, :]).index(c.most_common(1)[0][0])
                    stack_weights[x, y, z, first_majority_index] = 1.0

    return stack_weights


def get_uncertain_values_mask(stack_weights):
    # input are numpy array - as intermediate passage.
    uncertain_mask = np.zeros(stack_weights.shape[:-1], dtype=np.float64)
    for x in xrange(stack_weights.shape[0]):
        for y in xrange(stack_weights.shape[1]):
            for z in xrange(stack_weights.shape[2]):
                if 1.0 not in list(stack_weights[x, y, z, :]):
                    uncertain_mask[x, y, z] = 1
    return uncertain_mask


def from_weights_and_segmentations_get_the_final_segmentation(stack_segmentations, stack_weights, extra_label=254):
    # input are numpy array - prototype, very slow!
    ans = np.zeros_like(stack_segmentations[..., 0])
    for x in xrange(ans.shape[0]):
        for y in xrange(ans.shape[1]):
            for z in xrange(ans.shape[2]):
                label = (list(stack_segmentations[x, y, z, :]) + [extra_label]).index(np.max(stack_weights[x, y, z, :]))
                ans[x, y, z] = label
    return ans


def simple_majority_voting(stack_segmentations, stack_warped, target_subject):

    ans = np.zeros_like(stack_segmentations[..., 0]).astype(np.int16)

    for x in xrange(100, stack_segmentations.shape[0]):
        for y in xrange(100, stack_segmentations.shape[1]):
            for z in xrange(100, stack_segmentations.shape[2]):
                c = Counter(list(stack_segmentations[x, y, z, :]))
                if c.most_common(1)[0][1] >= 2:  # number of occurrences of the most common is >= threshold
                    ans[x, y, z] = c.most_common(1)[0][0]
                else:
                    # LNCC
                    data_target = []
                    data_im0 = []
                    data_im1 = []
                    data_im2 = []
                    for xi in xrange(-5, 5):
                        for yi in xrange(-5, 5):
                            for zi in xrange(-5, 5):
                                if (x - xi) ** 2 + (y - yi) ** 2 + (z - zi) ** 2 < 5:
                                    data_target.append(target_subject[x - xi, y - yi, z - zi])
                                    data_im0.append(stack_warped[x - xi, y - yi, z - zi, 0])
                                    data_im1.append(stack_warped[x - xi, y - yi, z - zi, 1])
                                    data_im2.append(stack_warped[x - xi, y - yi, z - zi, 2])

                    ncc_0 = (np.array(data_target) / float(np.linalg.norm(np.array(data_target))) ).dot( np.array(data_im0) / float(np.linalg.norm(np.array(data_im0))) )
                    ncc_1 = (np.array(data_target) / float(np.linalg.norm(np.array(data_target))) ).dot( np.array(data_im1) / float(np.linalg.norm(np.array(data_im1))) )
                    ncc_2 = (np.array(data_target) / float(np.linalg.norm(np.array(data_target))) ).dot( np.array(data_im2) / float(np.linalg.norm(np.array(data_im2))) )
                    pos_max = [ncc_0, ncc_1, ncc_2].index(np.max([ncc_0, ncc_1, ncc_2]))
                    print x, y, z
                    print [ncc_0, ncc_1, ncc_2], pos_max
                    ans[x, y, z] = stack_segmentations[x, y, z, pos_max]

    return ans

# paths to segmentations:

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

print 'Majority voting started:'
ans = simple_majority_voting(stack_seg, stack_warp, im_T1.get_data())

print ans.shape

im_lncc_maj_voting = set_new_data(im_seg, ans)
nib.save(im_lncc_maj_voting, jph(pfo_experiments, 'ans.nii.gz'))





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

