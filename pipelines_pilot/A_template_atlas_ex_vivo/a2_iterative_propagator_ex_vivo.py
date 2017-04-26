# draft code. To be optimised for a varied number of subjects.

"""
Propagate subject 1,2,3 on subject 4 and then select the best with a
majority voting.

"""

import os
from os.path import join as jph

from definitions import root_pilot_study
from tools.auxiliary.utils import print_and_run, grab_a_timepoint_path
from labels_manager.main import LabelsManager

root_pilot_study_ex_vivo = jph(root_pilot_study, 'A_templ_atlas_ex_vivo')

source_subjects = ['1305', '1702', '1805', '2002', '1201', '1203', '1404', '1507', '1510', '2502']
source_modalities = ['T1', 'FA', 'MD', 'S0', 'V1']
target_subject = '2503'


steps_map = {'Create intermediate folders'           : True,
             'Aff alignment'                         : True,
             'Propagate transformation to atlas aff' : True,
             'Propagate transformation to mask aff'  : True,
             'Get differential BFC'                  : True,
             'N-rig alignment of BFC'                : True,
             'Propagate to target n-rig'             : True,
             'Smooth result'                         : True,
             'Propagate to other modalities'         : False,
             'Generate stack'                        : True,  # phase 2 from here
             'Fuse'                                  : True}


safety_on = False

study_tag = '_st1'  # st1 : no 15xx
test_tag = '_test2_'  # with smol in the pre-processing.

pfo_target = jph(root_pilot_study_ex_vivo, target_subject)
pfo_segmentations = jph(root_pilot_study, 'A_templ_atlas_ex_vivo', target_subject, 'segmentations')
pfo_intermediate = jph(pfo_segmentations, 'z_gpwise_interm' + study_tag)
pfo_fused = jph(pfo_segmentations, 'z_lab_fusion' + study_tag )


if steps_map['Create intermediate folders']:
    print_and_run('mkdir -p {0} '.format(pfo_intermediate), safety_on=safety_on)


for sj in source_subjects:

    mod = 'T1'  # Only T1 modality at the moment

    pfo_source = jph(root_pilot_study_ex_vivo, sj)

    # input
    pfi_target                        = jph(pfo_target, 'all_modalities', target_subject + '_' + mod + '.nii.gz')
    pfi_target_roi_registration_masks = jph(pfo_target, 'masks', target_subject + '_roi_registration_mask.nii.gz')

    pfi_template_sj                   = jph(pfo_source, 'all_modalities', sj + '_' + mod + '.nii.gz')
    pfi_atlas_sj                      = jph(pfo_source, 'segmentations', 'approved', sj + '_propagate_me.nii.gz')
    pfi_mask_sj                       = jph(pfo_source, 'masks', sj + '_roi_registration_mask.nii.gz')

    # intermediate
    pfi_affine_transf            = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_affine_transf.txt')
    pfi_affine_transf_sj         = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_affine_warped.nii.gz')
    pfi_atlas_affine_registered  = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_atlas_affine_registered.nii.gz')
    pfi_mask_affine_registered   = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_mask_affine_registered.nii.gz')
    pfi_diff_bfc_target          = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_bfc_template.nii.gz')
    pfi_diff_bfc_subject         = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_bfc_subject.nii.gz')
    pfi_diff_bfc_n_rig_cpp       = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_bfc_cpp.nii.gz')
    pfi_diff_bfc_n_rig_res       = jph(pfo_intermediate, sj + '_' + mod + '_on_' + target_subject + '_bfc_res.nii.gz')

    # output
    smol = 1.2

    pfi_propagated_subject_on_target_anatomy = jph(pfo_intermediate,
                                                   'res_' + sj + '_' + mod + '_on_' + target_subject + '_subject_on_target_anatomy' + test_tag + '.nii.gz')
    pfi_propagated_subject_on_target_segm = jph(pfo_intermediate, 'res_' + sj + '_' + mod + '_on_' + target_subject + '_subject_on_target_segm' + test_tag + '.nii.gz')
    pfi_propagated_subject_on_target_segm_smol = jph(pfo_intermediate, 'res_' + sj + '_' + mod + '_on_' + target_subject + '_subject_on_target_segm_smol' + test_tag + '.nii.gz')

    list_pfi_input = [pfi_target, pfi_target_roi_registration_masks, pfi_template_sj, pfi_atlas_sj, pfi_mask_sj]

    for p in list_pfi_input:
        if not os.path.exists(p):
            raise IOError('Pfi {} does not exist. '.format(p))

    if steps_map['Aff alignment']:

        print '\n Affine alignment: source {} \n\n'.format(sj)

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} '.format(
               pfi_target, pfi_target_roi_registration_masks,
               pfi_template_sj, pfi_mask_sj, pfi_affine_transf, pfi_affine_transf_sj)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate transformation to atlas aff']:

        print '\n Propagate transformation to atlas aff: source {} \n\n'.format(sj)

        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_atlas_sj, pfi_affine_transf, pfi_atlas_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate transformation to mask aff']:

        print '\n Propagate transformation to mask aff: source {} \n\n'.format(sj)

        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_mask_sj, pfi_affine_transf, pfi_mask_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Get differential BFC']:

        print '\n Get differential BFC: source {} \n\n'.format(sj)

        bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
        cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
            pfi_target, pfi_target_roi_registration_masks,      pfi_diff_bfc_target,
            pfi_affine_transf_sj,    pfi_mask_affine_registered, pfi_diff_bfc_subject)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['N-rig alignment of BFC']:

        print '\n N-rig alignment of BFC: source {} \n\n'.format(sj)

        options = '-ln 2 -be 0.4'
        cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} {6}'.format(
            pfi_diff_bfc_target, pfi_target_roi_registration_masks, pfi_diff_bfc_subject, pfi_mask_affine_registered,
            pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res, options)

        print '\n\n'
        print cmd

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to target n-rig']:

        print '\n Propagate to target n-rig: source {} \n\n'.format(sj)

        cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                 pfi_target, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_subject_on_target_segm)

        cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 2'.format(
            pfi_target, pfi_affine_transf_sj, pfi_diff_bfc_n_rig_cpp, pfi_propagated_subject_on_target_anatomy)

        print_and_run(cmd0, safety_on=safety_on)
        print_and_run(cmd1, safety_on=safety_on)

    if steps_map['Smooth result']:

        print '\n Smooth result: source {} \n\n'.format(sj)

        cmd = 'seg_maths {0} -smol {1} {2}'.format(pfi_propagated_subject_on_target_segm, smol, pfi_propagated_subject_on_target_segm_smol)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to other modalities']:
        '''
        The same transformations obtained for the T1 are applied to the other modalities.
        '''
        print '\n Propagate to other modalities: source {} \n\n'.format(sj)

        for mod in list(set(source_modalities) - {'T1'}):

            pfi_target_mod = jph(pfo_target, 'all_modalities', target_subject + '_' + mod + '.nii.gz')
            pfi_sj_mod = jph(pfo_source, 'all_modalities', sj + '_' + mod + '.nii.gz')
            pfi_sj_mod_affine_registered = jph(pfo_intermediate,
                                               sj + '_' + mod + '_on_' + target_subject + '_rigid_subject_on_target_' + test_tag + '.nii.gz')
            pfi_sj_mod_non_rig_registered = jph(pfo_intermediate,
                                                sj + '_' + mod + '_on_' + target_subject + '_non_rigid_subject_on_target_' + test_tag + '.nii.gz')

            if mod == 'V1':
                # take only the first timepoint of the V1
                pfi_sj_mod_first_slice = jph(pfo_intermediate, sj + 'V1_first_direction.nii.gz')

                grab_a_timepoint_path(pfi_sj_mod, pfi_sj_mod_first_slice)
                mod = 'V1_first_direction'

            cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(
                pfi_target_mod, pfi_sj_mod, pfi_affine_transf, pfi_sj_mod_affine_registered)

            cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(
                pfi_target_mod, pfi_sj_mod_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_sj_mod_non_rig_registered)

            print_and_run(cmd0, safety_on=safety_on)
            print_and_run(cmd1, safety_on=safety_on)

""" Generate stacks and fuse: """

list_pfi_stack = []

if steps_map['Generate stack']:

    print '\n Generate stack \n\n'

    os.system('mkdir -p {0}'.format(pfo_fused))

    list_pfi_segmentations = [jph(pfo_intermediate, 'res_' + sj + '_T1_on_' + target_subject +
                                  '_subject_on_target_segm_smol' + test_tag + '.nii.gz')  # smol segmentation
                              for sj in source_subjects]

    list_pfi_warped = [jph(pfo_intermediate, 'res_' + sj + '_T1_on_' + target_subject + '_subject_on_target_anatomy' + test_tag + '.nii.gz')
                              for sj in source_subjects]

    print list_pfi_segmentations
    print list_pfi_warped

    for pfi_file in list_pfi_segmentations:
        if not os.path.exists(pfi_file):
            raise IOError('File {} does not exists '.format(pfi_file))

    for pfi_file in list_pfi_warped:
        if not os.path.exists(pfi_file):
            raise IOError('File {} does not exists '.format(pfi_file))

    lm = LabelsManager(pfo_intermediate, pfo_fused)
    pfi_target, pfi_result, pfi_4d_seg, pfi_4d_warp = lm.fuse.seg_LabFusion(pfi_target=jph(pfo_target, 'all_modalities',
                                                                                           target_subject + '_T1.nii.gz'),
                                                                      pfi_result='',
                                                                      list_pfi_segmentations=list_pfi_segmentations,
                                                                      list_pfi_warped=list_pfi_warped,
                                                                      options='',
                                                                      prepare_data_only=True)
    print pfi_target, pfi_result, pfi_4d_seg, pfi_4d_warp


pfi_target = jph(pfo_target, 'all_modalities', target_subject + '_T1.nii.gz')
pfi_4d_seg = jph(pfo_fused, 'res_4d_seg.nii.gz')
pfi_4d_warp = jph(pfo_fused, 'res_4d_warp.nii.gz')


if steps_map['Fuse']:

    print '\n Fuse \n\n'

    # Majority voting:
    pfi_output_MV = jph(pfo_fused, 'output_fusion_MV.nii.gz')
    cmd_mv = 'seg_LabFusion -in {0} -out {1} -MV'.format(pfi_4d_seg, pfi_output_MV)
    print cmd_mv
    os.system(cmd_mv)

    # # STAPLE:
    # pfi_output_STAPLE = jph(pfo_fused, 'output_STAPLE.nii.gz')
    # cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1} '.format(pfi_4d_seg, pfi_output_STAPLE)
    # print cmd_staple
    # os.system(cmd_staple)

    # STEPS:
    pfi_output_STEPS = jph(pfo_fused, 'output_fusion_STEPS_3_3_beta2p0.nii.gz')
    cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -MRF_beta {6} -prop_update'.format(pfi_4d_seg,
                                                                                                      pfi_output_STEPS,
                                                                                                      str(3),
                                                                                                      str(3),
                                                                                                      pfi_target,
                                                                                                      pfi_4d_warp,
                                                                                                      str(4.0))  # 4.0
    print cmd_steps
    os.system(cmd_steps)
