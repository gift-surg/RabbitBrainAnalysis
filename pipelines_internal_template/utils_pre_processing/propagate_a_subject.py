"""
Propagate a subject segmentation (starting subject) to another subject (destination subject)
"""
import numpy as np
from os.path import join as jph
import copy
import nibabel as nib
import os

from tools.definitions import root_pilot_study

from tools.auxiliary.multichannel import generate_multichannel_paths
from tools.auxiliary.utils import reproduce_slice_fourth_dimension_path
from tools.auxiliary.utils import set_new_data, print_and_run


subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']

sj_starting = '1305'
sj_destination = '1805'

# input
pfo_sj_starting = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj_starting)
pfi_starting_subject = jph(pfo_sj_starting, 'all_modalities', sj_starting + '_T1.nii.gz')
pfi_starting_atlas = jph(pfo_sj_starting, 'segmentations', 'approved', sj_starting + '_propagate_me.nii.gz')
pfi_starting_mask_aff = jph(pfo_sj_starting, 'masks', sj_starting + '_roi_registration_mask.nii.gz')
pfi_starting_mask_nrig = jph(pfo_sj_starting, 'masks', sj_starting + '_mask_special.nii.gz')

pfi_to_be_tested = [pfo_sj_starting, pfi_starting_subject, pfi_starting_atlas, pfi_starting_mask_aff, pfi_starting_mask_nrig]

for path in pfi_to_be_tested:
    if not os.path.exists(path):
        raise IOError('Input file {} does not exist.'.format(path))

pfo_sj_destination = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj_destination)
pfi_destination_subject = jph(pfo_sj_destination, 'all_modalities', sj_destination + '_T1.nii.gz')
pfi_destination_mask_aff = jph(pfo_sj_destination, 'masks', sj_destination + '_roi_registration_mask.nii.gz')
pfi_destination_masks_nrig = jph(pfo_sj_destination, 'masks', sj_destination + '_mask_special.nii.gz')


# output:
test_tag = '_from_' + sj_starting + '_t6'
pfi_propagated_segmentation = jph(pfo_sj_destination, 'segmentations', 'automatic', sj_destination + '_prop_segm' + test_tag + '.nii.gz')

# intermediate passages
pfo_intermediate_steps = jph(pfo_sj_destination, 'segmentations', 'automatic', 'z_segm_propag_passages')

pfi_affine_transf = jph(pfo_intermediate_steps, 'ref_' + sj_destination + '_flo_' + sj_starting + '_aff.txt')
pfi_affine_res = jph(pfo_intermediate_steps, 'ref_' + sj_destination + '_flo_' + sj_starting + '_aff.nii.gz')

pfi_atlas_affine_registered = jph(pfo_intermediate_steps, sj_starting + '_atlas_affine_registered_on_' + sj_destination + '.nii.gz')

pfi_diff_bfc_starting = jph(pfo_intermediate_steps, 'diff_bfc_' + sj_starting + '.nii.gz')
pfi_diff_bfc_destination = jph(pfo_intermediate_steps, 'diff_bfc_' + sj_destination + '.nii.gz')

pfi_diff_bfc_n_rig_cpp = jph(pfo_intermediate_steps, 'diff_bfc_' + sj_starting + '_on_' + sj_destination + '_nrig_cpp.nii.gz')
pfi_diff_bfc_n_rig_res = jph(pfo_intermediate_steps, 'diff_bfc_' + sj_starting + '_on_' + sj_destination + '_nrig.nii.gz')

safety_on = False

""" Steps manager """

steps_map = {'Aff alignment'                  : True,
             'Propagate to template aff'      : True,
             'Get differential BFC'           : True,
             'N-rig alignment of BFC'         : True,
             'Propagate to template n-rig'    : True}

""" PIPELINE   """


print '\n######################\n'
print 'Pipeline started: propagation from ' + sj_starting + ' to ' + sj_destination
print '\n######################\n\n\n'


cmd = 'mkdir -p {}'.format(pfo_intermediate_steps)
print_and_run(cmd)

if steps_map['Aff alignment']:

    cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5}'.format(
           pfi_destination_subject, pfi_destination_mask_aff,
           pfi_starting_subject, pfi_starting_mask_aff,
           pfi_affine_transf, pfi_affine_res)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['Propagate to template aff']:

    cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
             pfi_destination_subject, pfi_starting_atlas, pfi_affine_transf, pfi_atlas_affine_registered)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['Get differential BFC']:

    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
    cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
    pfi_affine_res,           pfi_starting_mask_nrig,               pfi_diff_bfc_starting,
    pfi_destination_subject,  pfi_destination_masks_nrig, pfi_diff_bfc_destination)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['N-rig alignment of BFC']:

    cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} -vel'.format(
        pfi_diff_bfc_destination, pfi_destination_masks_nrig, pfi_diff_bfc_starting, pfi_starting_mask_nrig,
        pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['Propagate to template n-rig']:

    cmd = 'reg_resample -ref {0} -flo {1} -cpp {2} -res {3} -inter 0'.format(
             pfi_destination_subject, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_segmentation)

    print_and_run(cmd, safety_on=safety_on)


print '\n######################\n'
print 'Pipeline terminated: propagation from ' + sj_starting + ' to ' + sj_destination
print '\n######################\n\n\n'

# print_and_run
'''
t1 only roi_registration_mask : not compensating enough for the non-rigid deformations. (aff default, nrig -be 0.8 -ln 2 -maxit 250)
t2 xxx only special mask, failed aff (aff default, nrig -be 0.8 -ln 2 -maxit 250)
t3 XXX only special mask, failed aff (aff -ln 2 -lp 1, nrig -be 0.8 -ln 2 -maxit 250)
------
t4 aff mask + nrig mask special (aff -ln 2 -lp 1, nrig -be 0.8 -ln 2 -maxit 250)
t5 aff mask + nrig mask special (aff default, nrig -be 0.8 -ln 2 -maxit 250)
t6 aff mask + nrig mask special (aff default, nrig -vel)
'''
