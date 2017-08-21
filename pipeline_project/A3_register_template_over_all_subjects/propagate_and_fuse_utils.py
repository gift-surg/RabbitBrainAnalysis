"""
Propagate subject 1,2,3 (source_subjects) on subject 4 (target_subject) and then fuse them with a STAPLE technique.
"""
import os
from os.path import join as jph
import pickle
from tools.auxiliary.utils import adjust_header_from_transformations, print_and_run
from tools.definitions import pfo_subjects_parameters
from pipeline_project.A0_main.subject_parameters_manager import propagate_me_level


def rigid_orientation_from_histo_to_given_coordinates(sj_source, pfo_source, sj_target, pfo_target, controller):
    """
    For the subjects that are used to build the template, from histological coordinates to bicommissural.
    Directly save in the target folder <group>/<category>/
    :return:
    """
    assert os.path.exists(pfo_source)
    assert os.path.exists(pfo_target)
    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_source), 'r'))

    pfo_mod = jph(pfo_target, 'mod')
    pfo_segm = jph(pfo_target, 'segm')
    pfo_mask = jph(pfo_target, 'z_mask')
    for p in [pfo_mod, pfo_segm, pfo_mask]:
        assert os.path.exists(p)
    pfo_tmp = jph(pfo_target, 'z_tmp', 'z_templ')
    print_and_run('mkdir -p {}'.format(pfo_tmp))

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
        theta = sj_parameters['angles'][1]
        pfi_source_T1_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_bicomm_hd.nii.gz')
        pfi_source_segm_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_segm_bicomm_hd.nii.gz')
        pfi_source_reg_mask_bicomm_hd = jph(pfo_tmp, sj_source + '_templ_reg_mask_bicomm_hd.nii.gz')
        cmd0 = 'cp {0} {1}'.format(pfi_source_T1, pfi_source_T1_bicomm_hd)
        cmd1 = 'cp {0} {1}'.format(pfi_source_segm, pfi_source_segm_bicomm_hd)
        cmd2 = 'cp {0} {1}'.format(pfi_source_reg_mask, pfi_source_reg_mask_bicomm_hd)
        print_and_run(cmd0)
        print_and_run(cmd1)
        print_and_run(cmd2)
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
        print_and_run(cmd)

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

        print_and_run(cmd)

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
        print_and_run(cmd)

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
        print_and_run(cmd)

    if controller['save result']:
        print('- save result {} '.format(sj_target))
        pfi_subject_propagated_on_target_segm_smol = jph(pfo_tmp,
                                                         'final' + sj_source + 'over' + sj_target + '_segm_smol.nii.gz')
        assert os.path.exists(pfi_subject_propagated_on_target_segm_smol)
        pfi_final_result = jph(pfo_segm, sj_target + '_T1_segm.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_subject_propagated_on_target_segm_smol, pfi_final_result)
        print_and_run(cmd)


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
    print_and_run('mkdir -p {}'.format(pfo_tmp))
    # Input
    pfi_T1 = jph(pfo_mod, sj + '_T1.nii.gz')
    pfi_segm_T1 = jph(pfo_segm, sj + '_T1_segm.nii.gz')
    pfi_S0 = jph(pfo_mod, sj + '_S0.nii.gz')
    pfi_MSME = jph(pfo_mod, 'MSME_tp0', sj + '_MSME_bfc_tp0.nii.gz')
    pfi_MSME_up = jph(pfo_mod, 'MSME_tp0', sj + '_MSME_bfc_up_tp0.nii.gz')
    pfi_reg_mask_T1 = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
    pfi_reg_mask_S0 = jph(pfo_mask, sj + '_b0_reg_mask.nii.gz')  # get also the registration mask other than the roi?
    pfi_reg_mask_MSME = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
    assert os.path.exists(pfi_T1)
    assert os.path.exists(pfi_segm_T1)
    assert os.path.exists(pfi_reg_mask_T1)
    assert os.path.exists(pfi_reg_mask_S0)  # same as mask msme_up
    # assert os.path.exists(pfi_reg_mask_MSME_up)
    # Output:
    pfi_segm_S0      = jph(pfo_segm, sj + '_S0_segm.nii.gz')
    pfi_segm_MSME    = jph(pfo_segm, sj + '_MSME_segm.nii.gz')

    print('Rigid propagator inter modality {}'.format(sj))

    if controller['rig register to S0']:
        print('- rig register to S0 {}'.format(sj))
        pfi_rigid_transf_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_aff.txt')
        pfi_rigid_warp_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_warp.nii.gz')

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly  '.format(
            pfi_S0, pfi_reg_mask_S0, pfi_T1, pfi_reg_mask_T1, pfi_rigid_transf_to_s0, pfi_rigid_warp_to_s0)
        print(cmd)
        print_and_run(cmd)

    if controller['rig propagate to S0']:
        print('- rig propagate to S0 {}'.format(sj))
        pfi_rigid_transf_to_s0 = jph(pfo_tmp, sj + 'rigid_T1_to_s0_aff.txt')
        assert os.path.exists(pfi_rigid_transf_to_s0)
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_S0, pfi_segm_T1, pfi_rigid_transf_to_s0, pfi_segm_S0)
        print(cmd)
        print_and_run(cmd)

    if controller['rig register MSME_up to MSME']:
        # register MSME_up with MSME. - then use the S0 segmentation (same as MSME_up segmentation) to propagate on MSME
        print('- rig register to MSME_up {}'.format(sj))
        pfi_rigid_transf_to_msme_up = jph(pfo_tmp, sj + 'rigid_MSME_up_to_MSME_aff.txt')
        pfi_rigid_warp_to_msme_up = jph(pfo_tmp, sj + 'rigid_MSME_up_to_MSME_warp.nii.gz')
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly'.format(
            pfi_MSME, pfi_reg_mask_MSME, pfi_MSME_up, pfi_reg_mask_S0, pfi_rigid_transf_to_msme_up,
            pfi_rigid_warp_to_msme_up)
        os.system(cmd)

    if controller['rig propagate segm_S0 to MSME']:
        print('- rig propagate to MSME_up {}'.format(sj))
        pfi_rigid_transf_to_msme_up = jph(pfo_tmp, sj + 'rigid_MSME_up_to_MSME_aff.txt')
        assert os.path.exists(pfi_rigid_transf_to_msme_up)
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_MSME, pfi_segm_S0, pfi_rigid_transf_to_msme_up, pfi_segm_MSME)
        os.system(cmd)


def propagate_and_fuse_multimodal():
    pass
