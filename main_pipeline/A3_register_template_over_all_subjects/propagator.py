import os
from os.path import join as jph
import pickle

from labels_manager.main import LabelsManager

from main_pipeline.A0_main.subject_parameters_manager import propagate_me_level
from labels_manager.tools.aux_methods.utils import print_and_run
from labels_manager.tools.aux_methods.sanity_checks import check_path_validity
from tools.definitions import bfc_corrector_cmd, pfo_subjects_parameters

from tools.correctors.tmp import adjust_affine_header


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
    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))

    for sj_source in list_templ_subjects:
        assert os.path.exists(jph(pfo_templ_subjects, sj_source))
    # -- Generate intermediate and output folders:
    pfo_mod = jph(pfo_to_target, 'mod')
    pfo_segm = jph(pfo_to_target, 'segm')
    pfo_mask = jph(pfo_to_target, 'z_mask')
    for p in [pfo_mod, pfo_segm, pfo_mask]:
        assert os.path.exists(p)
    pfo_tmp = jph(pfo_to_target, 'z_tmp', 'z_templ')
    print_and_run('mkdir -p {}'.format(pfo_tmp))

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
            print_and_run(cmd0)
            print_and_run(cmd1)
            print_and_run(cmd2)
            theta = sj_parameters['angles'][1]

            adjust_affine_header(pfi_templ_sj_bicomm_header, pfi_templ_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
            adjust_affine_header(pfi_templ_segm_sj_bicomm_header, pfi_templ_segm_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
            adjust_affine_header(pfi_templ_reg_mask_sj_bicomm_header, pfi_templ_reg_mask_sj_bicomm_header,
                                               theta=theta, trasl=(0, 0, 0))
        if controller['aff alignment']:
            opt = ''
            print('- aff alignment, {} over {}'.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_templ_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_bicomm_hd.nii.gz')
            pfi_templ_reg_mask_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_reg_mask_bicomm_hd.nii.gz')
            assert check_path_validity(pfi_target)
            assert check_path_validity(pfi_target_roi_registration_masks)
            assert check_path_validity(pfi_templ_sj_bicomm_header)
            assert check_path_validity(pfi_templ_reg_mask_sj_bicomm_header)
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} {6}'.format(
                pfi_target, pfi_target_roi_registration_masks,
                pfi_templ_sj_bicomm_header, pfi_templ_reg_mask_sj_bicomm_header,
                pfi_affine_transf, pfi_affine_warp_sj, opt)
            print_and_run(cmd)

        if controller['Propagate aff to segm']:
            print('- Propagate aff to segm, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_segm_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_segm_bicomm_hd.nii.gz')
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            assert check_path_validity(pfi_target)
            assert check_path_validity(pfi_segm_sj_bicomm_header)
            assert check_path_validity(pfi_affine_transf)
            pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp,
                                                             'templ' + sj + 'over' + sj_target + '_segm.nii.gz')
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target, pfi_segm_sj_bicomm_header, pfi_affine_transf, pfi_templ_segm_aff_registered_on_sj_target)

            print_and_run(cmd)

        if controller['Propagate aff to mask']:
            print('-  Propagate aff to mask, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_templ_reg_mask_sj_bicomm_header = jph(pfo_tmp, sj + '_templ_reg_mask_bicomm_hd.nii.gz')
            pfi_affine_transf = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_transf_aff.txt')
            assert check_path_validity(pfi_target)
            assert check_path_validity(pfi_templ_reg_mask_sj_bicomm_header)
            assert check_path_validity(pfi_affine_transf)
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0 '.format(
                pfi_target, pfi_templ_reg_mask_sj_bicomm_header, pfi_affine_transf,
                pfi_templ_reg_mask_sj_aff_registered)
            print_and_run(cmd)

        if controller['Get differential BFC'] and not sj_parameters['category'] == 'in_vivo':
            # for the in-vivo there is no need for the differential BFC
            print('- Get differential BFC, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            assert os.path.exists(pfi_target)
            assert check_path_validity(pfi_target_roi_registration_masks)
            assert os.path.exists(pfi_affine_warp_sj)
            assert check_path_validity(pfi_templ_reg_mask_sj_aff_registered)
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
                pfi_target, pfi_target_roi_registration_masks, pfi_diff_bfc_target,
                pfi_affine_warp_sj, pfi_templ_reg_mask_sj_aff_registered, pfi_diff_bfc_subject)
            print_and_run(cmd)
            assert check_path_validity(pfi_diff_bfc_target)
            assert check_path_validity(pfi_diff_bfc_subject)
        elif controller['N-rig alignment']:  # if it has to create the element for the next step without BFC.
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            assert os.path.exists(pfi_target)
            assert check_path_validity(pfi_affine_warp_sj)
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            cmd0 = 'cp {0} {1}'.format(pfi_target, pfi_diff_bfc_target)
            cmd1 = 'cp {0} {1}'.format(pfi_affine_warp_sj, pfi_diff_bfc_subject)
            print_and_run(cmd0)
            print_and_run(cmd1)

        if controller['N-rig alignment']:
            print('- N-rig alignment, {} over {}'.format(sj, sj_target))
            pfi_diff_bfc_target = jph(pfo_tmp, 'bfc' + sj_target + '.nii.gz')
            pfi_target_roi_registration_masks = jph(pfo_mask, sj_target + '_T1_reg_mask.nii.gz')
            pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '.nii.gz')
            pfi_templ_reg_mask_sj_aff_registered = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_reg_mask.nii.gz')
            assert check_path_validity(pfi_diff_bfc_target)
            assert os.path.exists(pfi_target_roi_registration_masks)
            assert check_path_validity(pfi_diff_bfc_subject)
            assert os.path.exists(pfi_templ_reg_mask_sj_aff_registered)
            pfi_diff_bfc_n_rig_cpp = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_cpp.nii.gz')
            pfi_diff_bfc_n_rig_res = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_warp.nii.gz')
            options = '-ln 2 -be 0.5'
            if sj_parameters['category'] == 'in_vivo':
                options = '-ln 2 -be 0.8'

            cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} {6}'.format(
                pfi_diff_bfc_target, pfi_target_roi_registration_masks, pfi_diff_bfc_subject,
                pfi_templ_reg_mask_sj_aff_registered, pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res, options)
            print_and_run(cmd)

        if controller['Propagate to target n-rig']:
            print('- Propagate to target n-rig, {} over {} '.format(sj, sj_target))
            pfi_target = jph(pfo_mod, sj_target + '_T1.nii.gz')
            pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp,
                                                             'templ' + sj + 'over' + sj_target + '_segm.nii.gz')
            pfi_affine_warp_sj = jph(pfo_tmp, 'templ' + sj + 'over' + sj_target + '_warp_aff.nii.gz')
            pfi_diff_bfc_n_rig_cpp = jph(pfo_tmp, 'bfc' + sj + 'over' + sj_target + '_cpp.nii.gz')
            assert os.path.exists(pfi_target)
            assert os.path.exists(pfi_templ_segm_aff_registered_on_sj_target)
            assert check_path_validity(pfi_affine_warp_sj)
            assert check_path_validity(pfi_diff_bfc_n_rig_cpp)
            pfi_subject_propagated_on_target_segm = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm.nii.gz')
            pfi_subject_propagated_on_target_warp = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_warp.nii.gz')
            cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target, pfi_templ_segm_aff_registered_on_sj_target, pfi_diff_bfc_n_rig_cpp,
                pfi_subject_propagated_on_target_segm)
            cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 2'.format(
                pfi_target, pfi_affine_warp_sj, pfi_diff_bfc_n_rig_cpp, pfi_subject_propagated_on_target_warp)
            print_and_run(cmd0)
            print_and_run(cmd1)

        if controller['Smooth result']:
            print('- Smooth result, {} over {}'.format(sj, sj_target))
            pfi_subject_propagated_on_target_segm = jph(pfo_tmp, 'final' + sj + 'over' + sj_target + '_segm.nii.gz')
            assert check_path_validity(pfi_subject_propagated_on_target_segm)
            pfi_subject_propagated_on_target_segm_smol = jph(pfo_tmp,
                                                             'final' + sj + 'over' + sj_target + '_segm_smol.nii.gz')
            smol = 0.2
            if sj_parameters['category'] == 'in_vivo':
                smol = 0
            if smol > 0:
                cmd = 'seg_maths {0} -smol {1} {2}'.format(pfi_subject_propagated_on_target_segm, smol,
                                                           pfi_subject_propagated_on_target_segm_smol)
            else:
                cmd = 'cp {0} {1}'.format(pfi_subject_propagated_on_target_segm,
                                          pfi_subject_propagated_on_target_segm_smol)
            print_and_run(cmd)

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
        # move to relative path to avoid too long paths.
        here = os.getcwd()
        os.chdir(pfo_to_target)

        rel_pfi_target = jph('mod', sj_target + '_T1.nii.gz')
        rel_pfi_4d_seg = jph('z_tmp', 'z_templ', 'res_4d_seg.nii.gz')
        rel_pfi_4d_warp = jph('z_tmp', 'z_templ', 'res_4d_warp.nii.gz')
        assert check_path_validity(jph(pfo_to_target, rel_pfi_4d_seg))
        assert check_path_validity(jph(pfo_to_target, rel_pfi_4d_warp))
        assert check_path_validity(jph(pfo_to_target, rel_pfi_target))
        rel_pfi_output_MV = jph('z_tmp', 'z_templ', 'result_' + sj_target + '_MV.nii.gz')
        # Majority voting:
        cmd_mv = 'seg_LabFusion -in {0} -out {1} -MV'.format(rel_pfi_4d_seg, rel_pfi_output_MV)
        # print_and_run(cmd_mv, short_path_output=False)
        os.system(cmd_mv)
        assert check_path_validity(rel_pfi_output_MV, timeout=1000, interval=2)
        # STAPLE:
        rel_pfi_output_STAPLE = jph('z_tmp', 'z_templ', 'result_' + sj_target + '_STAPLE.nii.gz')
        cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1} '.format(rel_pfi_4d_seg, rel_pfi_output_STAPLE)
        os.system(cmd_staple)
        # print_and_run(cmd_staple, short_path_output=False)
        assert check_path_validity(jph(pfo_to_target, rel_pfi_output_STAPLE), timeout=5000, interval=5)
        # STEPS:
        rel_pfi_output_STEPS = jph('z_tmp', 'z_templ', 'result_' + sj_target + '_STEPS.nii.gz')
        cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -MRF_beta {6} -prop_update'.format(
            rel_pfi_4d_seg,
            rel_pfi_output_STEPS,
            str(3),
            str(3),
            rel_pfi_target,
            rel_pfi_4d_warp,
            str(4.0))
        os.system(cmd_steps)
        # print_and_run(cmd_steps, short_path_output=False)
        assert check_path_validity(jph(pfo_to_target, rel_pfi_output_STEPS), timeout=1000, interval=2)
        # go back where it has started.
        os.chdir(here)

    if controller['save result']:
        print('- save result {}'.format(sj_target))

        print('Selected segmentation : {}'.format(controller['dominant method']))

        if controller['dominant method'] == 'MV':
            pfi_segm = jph(pfo_tmp, 'result_' + sj_target + '_MV.nii.gz')
        elif controller['dominant method'] == 'STAPLE':
            pfi_segm = jph(pfo_tmp, 'result_' + sj_target + '_STAPLE.nii.gz')
        elif controller['dominant method'] == 'STEPS':
            pfi_segm = jph(pfo_tmp, 'result_' + sj_target + '_STEPS.nii.gz')
        else:
            pfi_segm = jph(pfo_tmp, 'result_' + sj_target + '_MV.nii.gz')
            print('Selected segmentation not specified - default MV used')

        assert check_path_validity(pfi_segm)
        pfi_final_result = jph(pfo_segm, sj_target + '_T1_segm.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_segm, pfi_final_result)
        print_and_run(cmd)
