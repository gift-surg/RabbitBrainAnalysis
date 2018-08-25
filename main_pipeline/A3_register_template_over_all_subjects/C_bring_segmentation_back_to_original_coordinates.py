""" -------------------
C) From the segmented chart in stereotaxic coordinates, the segmentations are moved back to
the
------------------- """
import os
from os.path import join as jph
import pickle

import nilabels as nis

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from tools.auxiliary.reorient_images_header import orient2std


def propagate_segmentation_in_original_space_per_subject(sj, controller):
    """
    Movign from the stereotaxic oriented chart to the original chart.
    The stereotaxic can be directly retrieved from the multi-atlas if sj is in the template
    or it can be a chart in the multi-atlas, or it can be retrived from the 'stereotaxic' folder in
    the subject folder (under A_data), after the
    :param sj:
    :param controller:
    :return:
    """

    print('\nfrom Stereotaxic orientation to original space - SUBJECT {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    folder_selected_segmentation = sj_parameters['names_architecture']['final_segm_strx']  # default 'automatic'
    suffix_selected_segmentation = sj_parameters['names_architecture']['suffix_segm']  # default 'MV_P2'

    pfo_root_sj_orig = jph(root_study_rabbits, 'A_data', study, category, sj)
    pfo_root_sj_strx = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic')

    pfo_mod_orig  = jph(pfo_root_sj_orig, 'mod')
    pfo_mask_orig = jph(pfo_root_sj_orig, 'masks')
    pfo_segm_orig = jph(pfo_root_sj_orig, 'segm')

    pfo_mod_strx  = jph(pfo_root_sj_strx, 'mod')
    pfo_mask_strx = jph(pfo_root_sj_strx, 'masks')
    pfo_segm_strx = jph(pfo_root_sj_strx, 'segm')

    pfo_tmp  = jph(pfo_root_sj_orig, 'z_tmp', 'z_propagator')

    print_and_run('mkdir -p {}'.format(pfo_segm_orig))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    # recover the source in stereotaxic coordinates (strx):
    if sj_parameters['in_atlas']:
        if study == 'W8':
            pfo_sj_atlas = jph(root_study_rabbits, 'A_MultiAtlas_W8', sj)
        elif study == 'ACS' or study == 'PTB' or study == 'TestStudy':
            pfo_sj_atlas = jph(root_study_rabbits, 'A_MultiAtlas', sj)
        else:
            raise IOError('Study for subject {} not feasible.'.format(sj))

        pfi_T1_strx          = jph(pfo_sj_atlas, 'mod', '{}_T1.nii.gz'.format(sj))
        pfi_T1_reg_mask_strx = jph(pfo_sj_atlas, 'masks', '{}_reg_mask.nii.gz'.format(sj))
        pfi_T1_segm_strx     = jph(pfo_sj_atlas, 'segm', '{}_segm.nii.gz'.format(sj))
    else:
        pfi_T1_strx          = jph(pfo_mod_strx, '{}_T1.nii.gz'.format(sj))
        pfi_T1_reg_mask_strx = jph(pfo_mask_strx, '{}_T1_reg_mask.nii.gz'.format(sj))

        if folder_selected_segmentation == 'automatic':
            pfo_segmentation_strx = jph(pfo_segm_strx, 'automatic')
        else:
            pfo_segmentation_strx = pfo_segm_strx

        pfi_T1_segm_strx = jph(pfo_segmentation_strx, '{}_{}.nii.gz'.format(sj, suffix_selected_segmentation))

    for p in [pfi_T1_strx, pfi_T1_reg_mask_strx, pfi_T1_segm_strx]:
        assert os.path.exists(p), p

    # --> INTRA-modal segmentation:
    if controller['Header_alignment_T1strx_to_T1orig']:
        print('-> Align header T1strx to origin')
        # output header orientati:
        pfi_T1_strx_hdo          = jph(pfo_tmp, '{}_T1_strx_hdo.nii.gz'.format(sj))
        pfi_T1_reg_mask_strx_hdo = jph(pfo_tmp, '{}_T1_reg_mask_strx_hdo.nii.gz'.format(sj))
        pfi_T1_segm_strx_hdo     = jph(pfo_tmp, '{}_T1_segm_strx_hdo.nii.gz'.format(sj))

        angles = sj_parameters['angles']
        if isinstance(angles[0], list):
            pitch_theta = angles[0][1]
        else:
            pitch_theta = angles[1]

        for strx, strx_hdo in zip([pfi_T1_strx, pfi_T1_reg_mask_strx, pfi_T1_segm_strx],
                                  [pfi_T1_strx_hdo, pfi_T1_reg_mask_strx_hdo, pfi_T1_segm_strx_hdo]):
            cmd = 'cp {0} {1}'.format(strx, strx_hdo)
            print_and_run(cmd)
            if pitch_theta != 0:
                nis_app = nis.App()
                nis_app.header.apply_small_rotation(strx_hdo, strx_hdo,
                                                    angle=pitch_theta, principal_axis='pitch')

    if controller['Rigid_T1strx_to_T1orig']:
        print('-> Align T1strx_hdo (header oriented) to origin')
        # fixed
        pfi_T1_origin          = jph(pfo_mod_orig, '{}_T1.nii.gz'.format(sj))
        pfi_T1_reg_mask_origin = jph(pfo_mask_orig, '{}_T1_reg_mask.nii.gz'.format(sj))
        # moving
        pfi_T1_strx_hdo = jph(pfo_tmp, '{}_T1_strx_hdo.nii.gz'.format(sj))
        pfi_T1_reg_mask_strx_hdo = jph(pfo_tmp, '{}_T1_reg_mask_strx_hdo.nii.gz'.format(sj))
        assert os.path.exists(pfi_T1_origin), pfi_T1_origin
        assert os.path.exists(pfi_T1_reg_mask_origin), pfi_T1_reg_mask_origin
        assert os.path.exists(pfi_T1_strx_hdo), pfi_T1_strx_hdo
        assert os.path.exists(pfi_T1_reg_mask_strx_hdo), pfi_T1_reg_mask_strx_hdo

        pfi_transformation = jph(pfo_tmp, 'T1_strx_to_origin.txt')
        pfi_warped_T1_rigid = jph(pfo_tmp, 'T1_strx_to_origin_warped.nii.gz')

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} '.format(  # -rigOnly
            pfi_T1_origin, pfi_T1_reg_mask_origin, pfi_T1_strx_hdo, pfi_T1_reg_mask_strx_hdo,
            pfi_transformation, pfi_warped_T1_rigid)

        print_and_run(cmd)

    if controller['Propagate_T1_segm']:
        pfi_T1_origin        = jph(pfo_mod_orig, '{}_T1.nii.gz'.format(sj))
        pfi_T1_segm_strx_hdo = jph(pfo_tmp, '{}_T1_segm_strx_hdo.nii.gz'.format(sj))
        pfi_transformation   = jph(pfo_tmp, 'T1_strx_to_origin.txt')
        assert os.path.exists(pfi_T1_origin), pfi_T1_origin
        assert os.path.exists(pfi_T1_segm_strx_hdo), pfi_T1_segm_strx_hdo
        assert os.path.exists(pfi_transformation), pfi_transformation

        pfi_warped_T1_segm = jph(pfo_segm_orig, '{}_T1_segm.nii.gz'.format(sj))

        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -omp {4} -inter 0'.format(
            pfi_T1_origin, pfi_T1_segm_strx_hdo,
            pfi_transformation, pfi_warped_T1_segm, num_cores_run)

        print_and_run(cmd)

    # --> INTER-modal segmentation propagation: -- from here we are only working with the original chart.
    if controller['Inter_modal_reg_S0']:
        # T1 to S0 - Reference is S0. Floating is T1

        # references:
        pfi_S0_origin          = jph(pfo_mod_orig, '{}_S0.nii.gz'.format(sj))
        pfi_S0_reg_mask_origin = jph(pfo_mask_orig, '{}_S0_reg_mask.nii.gz'.format(sj))

        angles = sj_parameters['angles']
        if isinstance(angles[0], list):  # Both S0 and T1 angles are specified: [[y,p,r], [y,p,r]]
            pitch_theta_T1 = angles[0][1]
            pitch_theta_S0 = angles[1][1]
            pitch_theta = pitch_theta_S0 - pitch_theta_T1

            # floating oriented header:
            pfi_T1_strx_hdoS0          = jph(pfo_tmp, '{}_T1_strx_hdoS0.nii.gz'.format(sj))
            pfi_T1_reg_mask_strx_hdoS0 = jph(pfo_tmp, '{}_T1_reg_mask_strx_hdoS0.nii.gz'.format(sj))
            pfi_T1_segm_strx_hdoS0     = jph(pfo_tmp, '{}_T1_segm_strx_hdoS0.nii.gz'.format(sj))

            for strx, strx_hdo in zip([pfi_T1_strx, pfi_T1_reg_mask_strx, pfi_T1_segm_strx],
                                      [pfi_T1_strx_hdoS0, pfi_T1_reg_mask_strx_hdoS0, pfi_T1_segm_strx_hdoS0]):
                cmd = 'cp {0} {1}'.format(strx, strx_hdo)
                print_and_run(cmd)
                if pitch_theta != 0:
                    nis_app = nis.App()
                    nis_app.header.apply_small_rotation(strx_hdo, strx_hdo,
                                                   angle=pitch_theta, principal_axis='pitch')

            pfi_transformation = jph(pfo_tmp, 'T1origin_to_S0origin.txt')
            pfi_warped_T1toS0_rigid = jph(pfo_tmp, 'T1origin_to_S0origin_warped.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
                pfi_S0_origin, pfi_S0_reg_mask_origin, pfi_T1_strx_hdoS0, pfi_T1_reg_mask_strx_hdoS0,
                pfi_transformation, pfi_warped_T1toS0_rigid, num_cores_run
            )
            print_and_run(cmd)

            # result:
            pfi_S0_segm = jph(pfo_segm_orig, '{}_S0_segm.nii.gz'.format(sj))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_S0_origin, pfi_T1_segm_strx_hdoS0, pfi_transformation, pfi_S0_segm)
            print_and_run(cmd)

        else:
            # floating not oriented header:
            pfi_transformation = jph(pfo_tmp, 'T1origin_to_S0origin.txt')
            pfi_warped_T1toS0_rigid = jph(pfo_tmp, 'T1origin_to_S0origin_warped.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
                pfi_S0_origin, pfi_S0_reg_mask_origin, pfi_T1_strx, pfi_T1_reg_mask_strx,
                pfi_transformation, pfi_warped_T1toS0_rigid, num_cores_run
            )
            print_and_run(cmd)

            # result:
            pfi_S0_segm = jph(pfo_segm_orig, '{}_S0_segm.nii.gz'.format(sj))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_S0_origin, pfi_T1_segm_strx, pfi_transformation, pfi_S0_segm)
            print_and_run(cmd)

    if controller['Inter_modal_reg_MSME']:
        # MSMEinS0 to MSME: reference is MSME, floating is MSMEinS0 same as S0.
        # (same strategy used as before - again hardcoded)

        # references:
        pfi_MSME_origin = jph(pfo_mod_orig, 'MSME_tp0', '{}_MSME_tp0.nii.gz'.format(sj))
        pfi_MSME_reg_mask_origin = jph(pfo_mask_orig, '{}_MSME_reg_mask.nii.gz'.format(sj))

        # for safety orient the input to standard:
        orient2std(pfi_MSME_origin, pfi_MSME_origin)
        orient2std(pfi_MSME_reg_mask_origin, pfi_MSME_reg_mask_origin)

        assert os.path.exists(pfi_MSME_origin)
        assert os.path.exists(pfi_MSME_reg_mask_origin)

        # floating
        pfi_MSMEinS0 = jph(pfo_mod_orig, 'MSME_tp0', '{}_MSMEinS0_tp0.nii.gz'.format(sj))
        pfi_MSMEinS0_reg_mask = jph(pfo_mask_orig, '{}_S0_reg_mask.nii.gz'.format(sj))
        pfi_MSMEinS0_segm = jph(pfo_segm_orig, '{}_S0_segm.nii.gz'.format(sj))

        angles = sj_parameters['angles']
        if isinstance(angles[0], list) and len(angles) == 3:  # all angles specified: [[y,p,r], [y,p,r], [y,p,r]]

            pitch_theta_S0 = angles[1][1]
            pitch_theta_MSME = angles[2][1]
            pitch_theta = pitch_theta_MSME - pitch_theta_S0

            # floating oriented header:
            pfi_MSMEinS0_hdoMSME = jph(pfo_tmp, '{}_MSMEinS0_strx_hdoS0.nii.gz'.format(sj))
            pfi_MSMEinS0_reg_mask_hdoMSME = jph(pfo_tmp, '{}_MSMEinS0_reg_mask_strx_hdoS0.nii.gz'.format(sj))
            pfi_MSMEinS0_segm_hdoMSME = jph(pfo_tmp, '{}_MSMEinS0_segm_strx_hdoS0.nii.gz'.format(sj))

            for strx, strx_hdo in zip([pfi_MSMEinS0, pfi_MSMEinS0_reg_mask, pfi_MSMEinS0_segm],
                                      [pfi_MSMEinS0_hdoMSME, pfi_MSMEinS0_reg_mask_hdoMSME, pfi_MSMEinS0_segm_hdoMSME]):
                cmd = 'cp {0} {1}'.format(strx, strx_hdo)
                print_and_run(cmd)
                if pitch_theta != 0:
                    nis_app = nis.App()
                    nis_app.header.apply_small_rotation(strx_hdo, strx_hdo,
                                                        angle=pitch_theta, principal_axis='pitch')

            pfi_transformation = jph(pfo_tmp, 'MSMEinS0_to_MSME.txt')
            pfi_warped_MSMEinS0_to_MSME_rigid = jph(pfo_tmp, 'MSMEinS0_to_MSME_warped.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
                pfi_MSME_origin, pfi_MSME_reg_mask_origin, pfi_MSMEinS0_hdoMSME, pfi_MSMEinS0_reg_mask_hdoMSME,
                pfi_transformation, pfi_warped_MSMEinS0_to_MSME_rigid, num_cores_run
            )
            print_and_run(cmd)

            # result:
            pfi_MSME_segm = jph(pfo_segm_orig, '{}_MSME_segm.nii.gz'.format(sj))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_MSME_origin, pfi_MSMEinS0_segm_hdoMSME, pfi_transformation, pfi_MSME_segm)
            print_and_run(cmd)

        else:
            pfi_transformation = jph(pfo_tmp, 'MSMEinS0_to_MSME.txt')
            pfi_warped_MSMEinS0_to_MSME_rigid = jph(pfo_tmp, 'MSMEinS0_to_MSME_warped.nii.gz')
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
                pfi_MSME_origin, pfi_MSME_reg_mask_origin, pfi_MSMEinS0, pfi_MSMEinS0_reg_mask,
                pfi_transformation, pfi_warped_MSMEinS0_to_MSME_rigid, num_cores_run
            )
            print_and_run(cmd)

            # result:
            pfi_MSME_segm = jph(pfo_segm_orig, '{}_MSME_segm.nii.gz'.format(sj))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_MSME_origin, pfi_MSMEinS0_segm, pfi_transformation, pfi_MSME_segm)
            print_and_run(cmd)


def propagate_segmentation_in_original_space_from_list(subj_list, controller):
    print '\n\n Move to stereotaxic coordinate from list {} \n'.format(subj_list)
    for sj in subj_list:
        propagate_segmentation_in_original_space_per_subject(sj, controller)

if __name__ == '__main__':
    print('Propagate from Stereotaxic orientation to original space, local run. ')

    controller_ = {
        'Header_alignment_T1strx_to_T1orig' : True,
        'Rigid_T1strx_to_T1orig'            : True,
        'Propagate_T1_segm'                 : True,
        'Inter_modal_reg_S0'                : True,
        'Inter_modal_reg_MSME'              : False}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['5302', '5508', '55BW', '5303']  # ['13102', '13201', '13202', '13401', '13402', '13403']
    lsm.update_ls()

    propagate_segmentation_in_original_space_from_list(lsm.ls, controller_)
