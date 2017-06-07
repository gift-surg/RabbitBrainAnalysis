"""
Propagate subject 1,2,3 (source_subjects) on subject 4 (target_subject) and then fuse them with a STAPLE technique.
"""

import os
from os.path import join as jph

from labels_manager.main import LabelsManager

from pipeline_project.A0_main.main_controller import subject, propagate_me_level
from tools.auxiliary.utils import adjust_header_from_transformations
from tools.definitions import root_study_rabbits, bfc_corrector_cmd

"""
Disregarding the modality or other issues, various options are allowed.
The parameters are provided subject-wise and are stored in the Utils file subjects.

"""


def propagate_all_to_one(sj_target, pfo_to_target, pfo_templ_subjects, list_templ_subjects, controller):
    """
    All the segmentations, and all the warped propagated in one single image and stored in a folder.
    :param sj_target:
    :param pfo_to_target:
    :param pfo_templ_subjects: subjects manually segmented. We want the T1 and their manual segmentation.
    :param list_templ_subjects:
    :param controller:
    :return:
    """
    if sj_target not in subject.keys():
        raise IOError('Subject parameters not known')
    for sj_source in list_templ_subjects:
        assert os.path.exists(jph(pfo_templ_subjects, sj_source))
    # -- Generate intermediate and output folders:
    pfo_mod = jph(pfo_to_target, 'mod')
    pfo_segm = jph(pfo_to_target, 'segm')
    pfo_mask = jph(pfo_to_target, 'z_mask')
    for p in [pfo_mod, pfo_segm, pfo_mask]:
        assert os.path.exists(p)
    pfo_tmp = jph(pfo_to_target, 'z_tmp', 'z_templ')
    os.system('mkdir -p {}'.format(pfo_tmp))

    print('Propagate all manually segmented to {}'.format(sj_target))

    for sj in list_templ_subjects:

        if controller['set header bicommissural']:
            print('- set header bicommissural, {} over {}'.format(sj, sj_target))
            pfi_templ_sj = jph(pfo_templ_subjects, sj, 'all_modalities', sj + '_T1.nii.gz')
            pfo_approved = jph(pfo_templ_subjects, sj, 'segm', 'approved',)
            pfi_templ_segm_sj = jph(pfo_approved, sj + '_propagate_me_' + str(propagate_me_level) + '.nii.gz')
            pfi_T1_roi_reg_mask_sj = jph(pfo_templ_subjects, sj, 'masks', sj + '_roi_registration_mask.nii.gz')
            assert os.path.exists(pfi_templ_sj)
            assert os.path.exists(pfi_templ_segm_sj)
            assert os.path.exists(pfi_T1_roi_reg_mask_sj)
            pfi_templ_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_bicomm_hd.nii.gz')
            pfi_templ_segm_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_segm_bicomm_hd.nii.gz')
            pfi_templ_reg_mask_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_reg_mask_bicomm_hd.nii.gz')
            cmd0 = 'cp {0} {1}'.format(pfi_templ_sj, pfi_templ_sj_bicomm_header)
            cmd1 = 'cp {0} {1}'.format(pfi_templ_segm_sj, pfi_templ_segm_sj_bicomm_header)
            cmd2 = 'cp {0} {1}'.format(pfi_T1_roi_reg_mask_sj, pfi_templ_reg_mask_sj_bicomm_header)
            os.system(cmd0)
            os.system(cmd1)
            os.system(cmd2)
            theta = subject[sj][1][0]

            adjust_header_from_transformations(pfi_templ_sj_bicomm_header, pfi_templ_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
            adjust_header_from_transformations(pfi_templ_segm_sj_bicomm_header, pfi_templ_segm_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
            adjust_header_from_transformations(pfi_templ_reg_mask_sj_bicomm_header, pfi_templ_reg_mask_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
        if controller['aff alignment']:

            opt = ''
            if subject[sj_target][0][1] == 'in_vivo':
                opt = ' -rigOnly -speeeeed '

            print('- aff alignment, {} over {}'.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_templ_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_bicomm_hd.nii.gz')
            pfi_templ_reg_mask_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_reg_mask_bicomm_hd.nii.gz')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_target_roi_registration_masks)
            assert os.path.exists(pfi_templ_sj_bicomm_header)
            assert os.path.exists(pfi_templ_reg_mask_sj_bicomm_header)
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} {6}'.format(
                pfi_target, pfi_target_roi_registration_masks,
                pfi_templ_sj_bicomm_header, pfi_templ_reg_mask_sj_bicomm_header, 
                pfi_affine_transf, pfi_affine_warp_sj, opt)
            os.system(cmd)

        if controller['Propagate aff to segm']:
            print('- Propagate aff to segm, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_segm_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_segm_bicomm_hd.nii.gz')
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_segm_sj_bicomm_header)
            assert os.path.exists(pfi_affine_transf)
            pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp, 
                                                             'templ' + sj + 'over' + sj_target + '_segm.nii.gz')
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target, pfi_segm_sj_bicomm_header, pfi_affine_transf, pfi_templ_segm_aff_registered_on_sj_target)

            os.system(cmd)

        if controller['Propagate aff to mask']:
            print('-  Propagate aff to mask, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_templ_reg_mask_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_reg_mask_bicomm_hd.nii.gz')
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_templ_reg_mask_sj_bicomm_header)
            assert os.path.exists(pfi_affine_transf)
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0 '.format(
                pfi_target, pfi_templ_reg_mask_sj_bicomm_header, pfi_affine_transf,
                pfi_templ_reg_mask_sj_aff_registered)
            os.system(cmd)

        if controller['Get differential BFC'] and not subject[sj_target][0][1] == 'in_vivo':
            # for the in-vivo there is no need for the differential BFC
            print('- Get differential BFC, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_target_roi_registration_masks)
            assert os.path.exists(pfi_affine_warp_sj)
            assert os.path.exists(pfi_templ_reg_mask_sj_aff_registered)
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
                pfi_target, pfi_target_roi_registration_masks, pfi_diff_bfc_target,
                pfi_affine_warp_sj, pfi_templ_reg_mask_sj_aff_registered, pfi_diff_bfc_subject)
            os.system(cmd)
        else:
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_affine_warp_sj)
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            cmd0 = 'cp {0} {1}'.format(pfi_target, pfi_diff_bfc_target)
            cmd1 = 'cp {0} {1}'.format(pfi_affine_warp_sj, pfi_diff_bfc_subject)
            os.system(cmd0)
            os.system(cmd1)

        if controller['N-rig alignment']:
            print('- N-rig alignment, {} over {}'.format(sj, sj_target))
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            assert os.path.exists(pfi_diff_bfc_target)
            assert os.path.exists(pfi_target_roi_registration_masks)
            assert os.path.exists(pfi_diff_bfc_subject)
            assert os.path.exists(pfi_templ_reg_mask_sj_aff_registered)
            pfi_diff_bfc_n_rig_cpp = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_cpp.nii.gz')
            pfi_diff_bfc_n_rig_res = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_warp.nii.gz')
            options = '-ln 2 -be 0.5'
            if subject[sj_target][0][1] == 'in_vivo':
                options = '-ln 2 -be 0.8'

            cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} {6}'.format(
                pfi_diff_bfc_target, pfi_target_roi_registration_masks, pfi_diff_bfc_subject,
                pfi_templ_reg_mask_sj_aff_registered, pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res, options)
            os.system(cmd)

        if controller['Propagate to target n-rig']:
            print('- Propagate to target n-rig, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp,
                                                             'templ' + sj + 'over' + sj_target + '_segm.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            pfi_diff_bfc_n_rig_cpp = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_cpp.nii.gz')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_templ_segm_aff_registered_on_sj_target)
            assert os.path.exists(pfi_affine_warp_sj)
            assert os.path.exists(pfi_diff_bfc_n_rig_cpp)
            pfi_subject_propagated_on_target_segm = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm.nii.gz')
            pfi_subject_propagated_on_target_warp = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_warp.nii.gz')
            cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target, pfi_templ_segm_aff_registered_on_sj_target, pfi_diff_bfc_n_rig_cpp,
                pfi_subject_propagated_on_target_segm)
            cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 2'.format(
                pfi_target, pfi_affine_warp_sj, pfi_diff_bfc_n_rig_cpp, pfi_subject_propagated_on_target_warp)
            os.system(cmd0)
            os.system(cmd1)

        if controller['Smooth result']:
            print('- Smooth result, {} over {}'.format(sj, sj_target))
            pfi_subject_propagated_on_target_segm = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm.nii.gz')
            assert os.path.exists(pfi_subject_propagated_on_target_segm)
            pfi_subject_propagated_on_target_segm_smol = jph(pfo_tmp,
                                                             'final' + sj + 'over' + sj_target + '_segm_smol.nii.gz')
            smol = 0.2
            if subject[sj_target][0][1] == 'in_vivo':
                smol = 0
            if smol > 0:
                cmd = 'seg_maths {0} -smol {1} {2}'.format(pfi_subject_propagated_on_target_segm, smol,
                                                           pfi_subject_propagated_on_target_segm_smol)
            else:
                cmd = 'cp {0} {1}'.format(pfi_subject_propagated_on_target_segm,
                                          pfi_subject_propagated_on_target_segm_smol)
            os.system(cmd)

    # <end for>

    if controller['Stack warps and segm']:
        print('- Stack warps and segm {} '.format(sj_target))

        list_pfi_segmentations = [jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm_smol.nii.gz')  # smol seg
                                  for sj in list_templ_subjects]

        list_pfi_warped = [jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm.nii.gz')  # warped
                           for sj in list_templ_subjects]

        for p in list_pfi_segmentations:
            if not os.path.exists(p):
                msg = 'File {} in the list of segmentations does not exists '.format(p)
                raise IOError(msg)

        for p in list_pfi_warped:
            if not os.path.exists(p):
                msg = 'File {} in the list of warped does not exists '.format(p)
                raise IOError(msg)

        lm = LabelsManager(pfo_tmp, pfo_tmp)
        pfi_target, pfi_result, pfi_4d_seg, pfi_4d_warp = lm.fuse.seg_LabFusion(
            pfi_target=jph(pfo_mod, sj_target + '_T1.nii.gz'),
            pfi_result='',
            list_pfi_segmentations=list_pfi_segmentations,
            list_pfi_warped=list_pfi_warped,
            options='',
            prepare_data_only=True)

        print pfi_target, pfi_result, pfi_4d_seg, pfi_4d_warp

    if controller['Fuse']:
        print('- Fuse {} '.format(sj_target))
        pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
        pfi_4d_seg = jph(pfo_tmp, 'res_4d_seg.nii.gz')
        pfi_4d_warp = jph(pfo_tmp, 'res_4d_warp.nii.gz')
        assert os.path.exists(pfi_4d_seg)
        assert os.path.exists(pfi_4d_warp)
        assert os.path.exists(pfi_target)
        pfi_output_MV = jph(pfo_tmp, 'result_' + sj_target + '_MV.nii.gz')
        pfi_output_STEPS = jph(pfo_tmp, 'result_' + sj_target + '_STEPS.nii.gz')
        # pfi_output_STAPLE = jph(pfo_tmp, 'RESULT_' + sj_target + '_STAPLE.nii.gz')
        # Majority voting:
        cmd_mv = 'seg_LabFusion -in {0} -out {1} -MV'.format(pfi_4d_seg, pfi_output_MV)
        os.system(cmd_mv)
        # STAPLE:
        # cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1} '.format(pfi_4d_seg, pfi_output_STAPLE)
        # os.system(cmd_staple)
        # STEPS:
        cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -MRF_beta {6} -prop_update'.format(
            pfi_4d_seg,
            pfi_output_STEPS,
            str(3),
            str(3),
            pfi_target,
            pfi_4d_warp,
            str(4.0))
        os.system(cmd_steps)

    if controller['save result']:
        print('- save result {}'.format(sj_target))
        pfi_segm_STEPS = jph(pfo_tmp, 'result_' + sj_target + '_STEPS.nii.gz')
        assert os.path.exists(pfi_segm_STEPS)
        pfi_final_result = jph(pfo_segm, sj_target + '_T1_segm.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_segm_STEPS, pfi_final_result)
        os.system(cmd)


def rigid_orientation_from_histo_to_given_coordinates(sj_source, pfo_source, sj_target, pfo_target, controller):
    """
    For the subjects that are used to build the template, from histological coordinates to bicommissural.
    Directly save in the target folder <group>/<category>/
    :return:
    """
    assert os.path.exists(pfo_source)
    assert os.path.exists(pfo_target)
    if sj_target not in subject.keys():
        raise IOError('Subject parameters not known')
    pfo_mod = jph(pfo_target, 'mod')
    pfo_segm = jph(pfo_target, 'segm')
    pfo_mask = jph(pfo_target, 'z_mask')
    for p in [pfo_mod, pfo_segm, pfo_mask]:
        assert os.path.exists(p)
    pfo_tmp = jph(pfo_target, 'z_tmp', 'z_templ')
    os.system('mkdir -p {}'.format(pfo_tmp))

    print('Rigid orientation from histological to given coordinates. {}'.format(sj_target))

    if controller['set header bicommissural']:
        print('- set header bicommissural {} '.format(sj_target))
        # for T1 and segm pass from histological to bicommissural
        pfi_source_T1 = jph(pfo_source, 'all_modalities', sj_source + '_T1.nii.gz')
        pfi_source_segm = jph(pfo_source,
                              'segm', 'approved', sj_source + '_propagate_me_' + str(propagate_me_level) + '.nii.gz')
        pfi_source_reg_mask = jph(pfo_source, 'masks', sj_source + '_roi_registration_mask.nii.gz')
        assert os.path.exists(pfi_source_T1), pfi_source_T1
        assert os.path.exists(pfi_source_segm), pfi_source_segm
        assert os.path.exists(pfi_source_reg_mask), pfi_source_reg_mask
        theta = subject[sj_source][1][0]
        pfi_source_T1_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_bicomm_hd.nii.gz')
        pfi_source_segm_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_segm_bicomm_hd.nii.gz')
        pfi_source_reg_mask_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_reg_mask_bicomm_hd.nii.gz')
        cmd0 = 'cp {0} {1}'.format(pfi_source_T1, pfi_source_T1_bicomm_hd)
        cmd1 = 'cp {0} {1}'.format(pfi_source_segm, pfi_source_segm_bicomm_hd)
        cmd2 = 'cp {0} {1}'.format(pfi_source_reg_mask, pfi_source_reg_mask_bicomm_hd)
        os.system(cmd0)
        os.system(cmd1)
        os.system(cmd2)
        adjust_header_from_transformations(pfi_source_T1_bicomm_hd, pfi_source_T1_bicomm_hd,
                                           theta=theta, trasl=(0, 0, 0))
        adjust_header_from_transformations(pfi_source_segm_bicomm_hd, pfi_source_segm_bicomm_hd,
                                           theta=theta, trasl=(0, 0, 0))
        adjust_header_from_transformations(pfi_source_reg_mask_bicomm_hd, pfi_source_reg_mask_bicomm_hd,
                                           theta=theta, trasl=(0, 0, 0))
    if controller['rig alignment']:
        print('- rig alignment {} '.format(sj_target))
        pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
        pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
        pfi_source_T1_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_bicomm_hd.nii.gz')
        pfi_source_reg_mask_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_reg_mask_bicomm_hd.nii.gz')
        assert os.path.exists(pfi_target)
        assert os.path.exists(pfi_target_roi_registration_masks)
        assert os.path.exists(pfi_source_T1_bicomm_hd)
        assert os.path.exists(pfi_source_reg_mask_bicomm_hd)
        pfi_affine_transf = jph(pfo_tmp, 'templ' + sj_source + 'over' + sj_target + '_transf_aff.txt')
        pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj_source + 'over' + sj_target + '_warp_aff.nii.gz')
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly'.format(
            pfi_target, pfi_target_roi_registration_masks,
            pfi_source_T1_bicomm_hd, pfi_source_reg_mask_bicomm_hd,
            pfi_affine_transf, pfi_affine_warp_sj)
        os.system(cmd)

    if controller['Propagate aff to segm']:
        print('- Propagate aff to segm {} '.format(sj_target))
        pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
        pfi_source_segm_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_segm_bicomm_hd.nii.gz')
        pfi_affine_transf = jph(pfo_tmp, 'templ' + sj_source + 'over' + sj_target + '_transf_aff.txt')
        assert os.path.exists(pfi_target)
        assert os.path.exists(pfi_source_segm_bicomm_hd)
        assert os.path.exists(pfi_affine_transf)
        pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp,
                                                         'templ' + sj_source + 'over' + sj_target + '_segm.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_target, pfi_source_segm_bicomm_hd, pfi_affine_transf, pfi_templ_segm_aff_registered_on_sj_target)

        os.system(cmd)

    if controller['Propagate aff to mask']:
        print('- Propagate aff to mask {} '.format(sj_target))
        pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
        pfi_source_reg_mask_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_reg_mask_bicomm_hd.nii.gz')
        pfi_affine_transf = jph(pfo_tmp, 'templ' + sj_source + 'over' + sj_target + '_transf_aff.txt')
        assert os.path.exists(pfi_target)
        assert os.path.exists(pfi_source_reg_mask_bicomm_hd)
        assert os.path.exists(pfi_affine_transf)
        pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp,
                                                   'templ' + sj_source + 'over' + sj_target + '_reg_mask.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_target, pfi_source_reg_mask_bicomm_hd, pfi_affine_transf, pfi_templ_reg_mask_sj_aff_registered)
        os.system(cmd)

    if controller['Smooth']:
        print('- Smooth {} '.format(sj_target))
        pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp,
                                                         'templ' + sj_source + 'over' + sj_target + '_segm.nii.gz')
        assert os.path.exists(pfi_templ_segm_aff_registered_on_sj_target)
        pfi_subject_propagated_on_target_segm_smol = jph(pfo_tmp,
                                                         'final' + sj_source + 'over' + sj_target + '_segm_smol.nii.gz')
        smol = 0.2
        if smol > 0:
            cmd = 'seg_maths {0} -smol {1} {2}'.format(pfi_templ_segm_aff_registered_on_sj_target, smol,
                                                       pfi_subject_propagated_on_target_segm_smol)
        else:
            cmd = 'cp {0} {1}'.format(pfi_templ_segm_aff_registered_on_sj_target,
                                      pfi_subject_propagated_on_target_segm_smol)
        os.system(cmd)

    if controller['save result']:
        print('- save result {} '.format(sj_target))
        pfi_subject_propagated_on_target_segm_smol = jph(pfo_tmp,
                                                         'final' + sj_source + 'over' + sj_target + '_segm_smol.nii.gz')
        assert os.path.exists(pfi_subject_propagated_on_target_segm_smol)
        pfi_final_result = jph(pfo_segm, sj_target + '_T1_segm.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_subject_propagated_on_target_segm_smol, pfi_final_result)
        os.system(cmd)


def rigid_propagation_inter_modality(sj, pfo_sj, controller):
    """
    When T1 is segmented, the same segmentation is rigidly propagated to MSME and S0 with this function.
    :param sj:
    :param pfo_sj:
    :param controller:
    :return:
    """
    assert os.path.exists(pfo_sj)
    pfo_mod = jph(pfo_sj, 'mod')
    pfo_segm = jph(pfo_sj, 'segm')
    pfo_mask = jph(pfo_sj, 'z_mask')
    for p in [pfo_mod, pfo_segm, pfo_mask]:
        assert os.path.exists(p)
    pfo_tmp = jph(pfo_sj, 'z_tmp', 'z_inter_mod_propag')
    os.system('mkdir -p {}'.format(pfo_tmp))
    # Input
    pfi_T1 = jph(pfo_mod, sj + '_T1.nii.gz')
    pfi_segm_T1 = jph(pfo_segm, sj + '_T1_segm.nii.gz')
    pfi_S0 = jph(pfo_mod, sj + '_S0.nii.gz')
    pfi_MSME_up = jph(pfo_mod, sj + '_MSME_up_1st.nii.gz')
    pfi_MSME = jph(pfo_mod, sj + '_MSME.nii.gz')
    pfi_reg_mask_T1 = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
    pfi_reg_mask_S0 = jph(pfo_mask, sj + '_b0_reg_mask.nii.gz')  # get also the registration mask other than the roi?
    # pfi_reg_mask_MSME_up = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
    assert os.path.exists(pfi_T1)
    assert os.path.exists(pfi_segm_T1)
    assert os.path.exists(pfi_reg_mask_T1)
    assert os.path.exists(pfi_reg_mask_S0)  # same as mask msme_up
    # assert os.path.exists(pfi_reg_mask_MSME_up)
    # Output
    pfi_segm_S0 = jph(pfo_segm, sj + '_S0_segm.nii.gz')
    # pfi_segm_MSME_up = jph(pfo_segm, sj + '_MSME_up_segm.nii.gz')
    pfi_segm_MSME = jph(pfo_segm, sj + '_MSME_segm.nii.gz')

    print('Rigid propagator inter modality {}'.format(sj))

    if controller['rig register to S0']:
        print('- rig register to S0 {}'.format(sj))
        pfi_rigid_transf_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_aff.txt')
        pfi_rigid_warp_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_warp.nii.gz')

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly  '.format(
            pfi_S0, pfi_reg_mask_S0, pfi_T1, pfi_reg_mask_T1, pfi_rigid_transf_to_s0, pfi_rigid_warp_to_s0)
        print(cmd)
        os.system(cmd)

    if controller['rig propagate to S0']:
        print('- rig propagate to S0 {}'.format(sj))
        pfi_rigid_transf_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_aff.txt')
        assert os.path.exists(pfi_rigid_transf_to_s0)
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_S0, pfi_segm_T1, pfi_rigid_transf_to_s0, pfi_segm_S0)
        print(cmd)
        os.system(cmd)

    # if controller['rig register to MSME_up']:
    #     print('- rig register to MSME_up {}'.format(sj))
    #     pfi_rigid_transf_to_msme_up = jph(pfo_tmp, sj + 'rigid_T1_to_MSME_aff.txt')
    #     pfi_rigid_warp_to_msme_up = jph(pfo_tmp, sj + 'rigid_T1_to_MSME_warp.nii.gz')
    #     cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly'.format(
    #         pfi_MSME_up, pfi_reg_mask_S0, pfi_T1, pfi_reg_mask_T1, pfi_rigid_transf_to_msme_up,
    #         pfi_rigid_warp_to_msme_up)
    #     os.system(cmd)
    #
    # if controller['rig propagate to MSME_up']:
    #     print('- rig propagate to MSME_up {}'.format(sj))
    #     pfi_rigid_transf_to_msme_up = jph(pfo_tmp, sj + 'rigid_T1_to_MSME_aff.txt')
    #     assert os.path.exists(pfi_rigid_transf_to_msme_up)
    #     cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
    #         pfi_MSME_up, pfi_segm_T1, pfi_rigid_transf_to_msme_up, pfi_segm_MSME_up)
    #     os.system(cmd)

    if controller['MSME_up to MSME']:
        print('- MSME_up to MSME {}'.format(sj))
        # the MSME_up segmentation is the same as S0 segmentation., and it is the same as the g-ratio segmentation.

        pfo_utils = jph(root_study_rabbits, 'A_data', 'Utils')
        pfi_id_transf = jph(pfo_utils, 'aff_id.txt')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_MSME, pfi_segm_S0, pfi_id_transf, pfi_segm_MSME)
        os.system(cmd)


def propagate_and_fuse_multimodal():
    pass
