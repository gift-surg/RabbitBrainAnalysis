# draft code. To be optimised for a varied number of subjects.

"""
Propagate subject 1,2,3 on subject 4 and then select the best with a
majority voting.
"""

import os
from os.path import join as jph

from definitions import root_pilot_study
from tools.auxiliary.utils import print_and_run


root_pilot_study_ex_vivo = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

source_subjects = ['1305', '1702', '1805']
target_subject = '2002'


steps_map = {'Create intermediate folders'           : True,
             'Aff alignment'                         : True,
             'Propagate transformation to atlas aff' : True,
             'Propagate transformation to mask aff'  : True,
             'Get differential BFC'           : True,
             'N-rig alignment of BFC'         : True,
             'Propagate to template n-rig'    : True,
             'Smooth result'                  : True}


safety_on = False


for sj in source_subjects:

    pfo_source = jph(root_pilot_study_ex_vivo, sj)
    pfo_target = jph(root_pilot_study_ex_vivo, target_subject)
    pfo_intermediate = jph(pfo_target, 'segmentations', 'z_groupwise_intermediate')

    # input
    pfi_target                        = jph(pfo_target, 'all_modalities', target_subject + '_T1.nii.gz')
    pfi_target_roi_registration_masks = jph(pfo_target, 'masks', target_subject + '_roi_registration_mask.nii.gz')

    pfi_template_sj                   = jph(pfo_source, 'all_modalities', sj + '_T1.nii.gz')
    pfi_atlas_sj                      = jph(pfo_source, 'segmentations', 'approved', sj + '_propagate_me.nii.gz')
    pfi_mask_sj                       = jph(pfo_source, 'masks', sj + '_roi_registration_mask.nii.gz')

    # intermediate
    pfi_affine_transf            = jph(pfo_intermediate, sj + 'on' + target_subject + '_affine_transf.txt')
    pfi_affine_transf_sj         = jph(pfo_intermediate, sj + 'on' + target_subject + '_affine_warped.nii.gz')
    pfi_atlas_affine_registered  = jph(pfo_intermediate, sj + 'on' + target_subject + '_atlas_affine_registered.nii.gz')
    pfi_mask_affine_registered   = jph(pfo_intermediate, sj + 'on' + target_subject + '_mask_affine_registered.nii.gz')
    pfi_diff_bfc_target          = jph(pfo_intermediate, sj + 'on' + target_subject + '_bfc_template.nii.gz')
    pfi_diff_bfc_subject         = jph(pfo_intermediate, sj + 'on' + target_subject + '_bfc_subject.nii.gz')
    pfi_diff_bfc_n_rig_cpp       = jph(pfo_intermediate, sj + 'on' + target_subject + '_bfc_cpp.nii.gz')
    pfi_diff_bfc_n_rig_res       = jph(pfo_intermediate, sj + 'on' + target_subject + '_bfc_res.nii.gz')

    # output
    test_tag = '_test_1'
    smol = 1.2
    pfo_results = jph(pfo_target, 'segmentations', 'automatic')
    pfi_propagated_prelim_templ = jph(pfo_results,
                                      sj + 'on' + target_subject + '_atlas_propagated' + test_tag + '.nii.gz')
    pfi_propagated_prelim_templ_smol = jph(pfo_results,
                                           sj + 'on' + target_subject + '_atlas_propagated_smol' + test_tag + '.nii.gz')

    list_pfi_input = [pfi_target, pfi_target_roi_registration_masks, pfi_template_sj, pfi_atlas_sj, pfi_mask_sj]
    for p in list_pfi_input:
        if not os.path.exists(p):
            raise IOError('Pfi {} does not exist. '.format(p))

    if steps_map['Create intermediate folders']:

        print_and_run('mkdir -p {0} '.format(pfo_intermediate), safety_on=safety_on)
        print_and_run('mkdir -p {0} '.format(pfo_results), safety_on=safety_on)

    if steps_map['Aff alignment']:

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} '.format(
               pfi_target, pfi_target_roi_registration_masks,
               pfi_template_sj, pfi_mask_sj, pfi_affine_transf, pfi_affine_transf_sj)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate transformation to atlas aff']:

        cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_atlas_sj, pfi_affine_transf, pfi_atlas_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate transformation to mask aff']:

        cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_mask_sj, pfi_affine_transf, pfi_mask_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Get differential BFC']:

        bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
        cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
            pfi_target, pfi_target_roi_registration_masks,      pfi_diff_bfc_target,
            pfi_affine_transf_sj,    pfi_mask_affine_registered, pfi_diff_bfc_subject)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['N-rig alignment of BFC']:

        cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} -be 0.8 -ln 2 -maxit 250'.format(
            pfi_diff_bfc_target, pfi_target_roi_registration_masks, pfi_diff_bfc_subject, pfi_mask_affine_registered,
            pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to template n-rig']:

        cmd = 'reg_resample -ref {0} -flo {1} -cpp {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_prelim_templ)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Smooth result']:

        cmd = 'seg_maths {0} -smol {1} {2}'.format(pfi_propagated_prelim_templ, smol, pfi_propagated_prelim_templ_smol)

        print_and_run(cmd, safety_on=safety_on)