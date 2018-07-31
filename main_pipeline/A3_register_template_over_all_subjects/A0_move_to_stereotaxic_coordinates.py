""" -------------------
A) re-orient the chart in stereotaxic coordinate.
------------------- """
import os
from os.path import join as jph
import pickle
import numpy as np
import nibabel as nib

from LABelsToolkit.main import LABelsToolkit

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_atlas, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from tools.auxiliary.multichannel import stack_a_list_of_images_from_list_pfi


def resample_A_on_B_path_z(pfi_B_reference, pfi_A_floating, pfi_A_resampled_B, pfo_tmp, inter=1):
    np.savetxt(jph(pfo_tmp, 'id.txt'), np.eye(4))
    cmd = 'reg_resample -ref {} -flo {} -aff {} -res {} -inter {}'.format(
        pfi_B_reference, pfi_A_floating, jph(pfo_tmp, 'id.txt'), pfi_A_resampled_B, inter)
    print_and_run(cmd)


def move_to_stereotaxic_coordinate_per_subject(sj, controller, options):
    print('\nProcessing T1 {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    pfo_sj_mod  = jph(pfo_sj, 'mod')
    pfo_sj_masks = jph(pfo_sj, 'masks')

    assert os.path.exists(pfo_sj_mod)
    assert os.path.exists(pfo_sj_masks)

    # reference atlas main modality and mask
    pfi_mod_reference_atlas = jph(options['Template_chart_path'], 'mod', '{0}_{1}.nii.gz'.format(
        options['Template_name'], 'T1'))
    pfi_reg_mask_reference_atlas = jph(options['Template_chart_path'], 'masks', '{0}_reg_mask.nii.gz'.format(
        options['Template_name']))

    assert os.path.exists(pfi_mod_reference_atlas), pfi_mod_reference_atlas
    assert os.path.exists(pfi_reg_mask_reference_atlas), pfi_reg_mask_reference_atlas

    pfo_tmp = jph(pfo_sj, 'z_tmp', 'z_sc_aligment'.format(sj))
    pfo_sc_sj = jph(pfo_sj, 'stereotaxic')
    pfo_sc_sj_mod = jph(pfo_sc_sj, 'mod')
    pfo_sc_sj_masks = jph(pfo_sc_sj, 'masks')

    subject_is_in_atlas = sj_parameters['in_atlas']

    if subject_is_in_atlas:
        pfo_sj_mod_in_atlas = jph(root_atlas, sj, 'mod')
        pfo_sj_masks_in_atlas = jph(root_atlas, sj, 'masks')
        pfo_sj_segm_in_atlas = jph(root_atlas, sj, 'segm')
        assert os.path.exists(pfo_sj_mod_in_atlas), pfo_sj_mod_in_atlas
        assert os.path.exists(pfo_sj_masks_in_atlas), pfo_sj_masks_in_atlas
        assert os.path.exists(pfo_sj_segm_in_atlas), pfo_sj_segm_in_atlas

        print_and_run('mkdir -p {}'.format(pfo_sc_sj))
        cmd = 'cp -r {} {}'.format(pfo_sj_mod_in_atlas, pfo_sc_sj)
        print_and_run(cmd)
        cmd = 'cp  -r {} {}'.format(pfo_sj_masks_in_atlas, pfo_sc_sj)
        print_and_run(cmd)
        cmd = 'cp -r {} {}'.format(pfo_sj_segm_in_atlas, pfo_sc_sj)
        print_and_run(cmd)
        return

    # Initialise folder structure in stereotaxic coordinates
    if controller['Initialise_sc_folder']:

        print_and_run('mkdir -p {}'.format(pfo_tmp))
        print_and_run('mkdir -p {}'.format(pfo_sc_sj))
        print_and_run('mkdir -p {}'.format(pfo_sc_sj_mod))
        print_and_run('mkdir -p {}'.format(pfo_sc_sj_masks))

    if controller['Register_T1']:

        print('Orient header histological T1 and reg-mask:')
        angles = sj_parameters['angles']
        if isinstance(angles[0], list):
            pitch_theta = -1 * angles[0][1]
        else:
            pitch_theta = -1 * angles[1]

        pfi_original_T1 = jph(pfo_sj_mod, '{0}_{1}.nii.gz'.format(sj, 'T1'))
        assert os.path.exists(pfi_original_T1), pfi_original_T1
        pfi_T1_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}.nii.gz'.format(sj, 'T1'))

        print_and_run('cp {} {}'.format(pfi_original_T1, pfi_T1_reoriented))
        if pitch_theta != 0:
            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_T1_reoriented, pfi_T1_reoriented, angle=pitch_theta,
                                           principal_axis='pitch')

        pfi_original_roi_mask_T1 = jph(pfo_sj_masks, '{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'roi_mask'))
        assert os.path.exists(pfi_original_roi_mask_T1), pfi_original_roi_mask_T1
        pfi_roi_mask_T1_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'roi_mask'))

        print_and_run('cp {} {}'.format(pfi_original_roi_mask_T1, pfi_roi_mask_T1_reoriented))
        if pitch_theta != 0:
            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_roi_mask_T1_reoriented, pfi_roi_mask_T1_reoriented,
                                           angle=pitch_theta, principal_axis='pitch')

        pfi_original_reg_mask_T1 = jph(pfo_sj_masks, '{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'reg_mask'))
        assert os.path.exists(pfi_original_reg_mask_T1), pfi_original_reg_mask_T1
        pfi_reg_mask_T1_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'reg_mask'))

        print_and_run('cp {} {}'.format(pfi_original_reg_mask_T1, pfi_reg_mask_T1_reoriented))
        if pitch_theta != 0:
            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_reg_mask_T1_reoriented,
                                           pfi_reg_mask_T1_reoriented,
                                           angle=pitch_theta, principal_axis='pitch')
            del lm

        print('Rigid registration T1:')
        pfi_transformation_T1_over_T1 = jph(pfo_tmp, 'trans_{0}_over_{1}_mod_{2}_rigid.txt'.format(
            sj, options['Template_name'], 'T1'))
        pfi_resampled_T1 = jph(pfo_sc_sj_mod, '{0}_T1.nii.gz'.format(sj))  # RESULT

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
            pfi_mod_reference_atlas, pfi_reg_mask_reference_atlas, pfi_T1_reoriented, pfi_reg_mask_T1_reoriented,
            pfi_transformation_T1_over_T1, pfi_resampled_T1, num_cores_run)
        print_and_run(cmd)

        del angles, pitch_theta, pfi_original_T1, pfi_T1_reoriented, pfi_original_reg_mask_T1, \
            pfi_reg_mask_T1_reoriented, pfi_transformation_T1_over_T1, pfi_resampled_T1, cmd

    if controller['Propagate_T1_masks']:
        print('Propagate T1 mask:')
        pfi_T1_in_sc = jph(pfo_sc_sj_mod, '{0}_T1.nii.gz'.format(sj))
        pfi_roi_mask_T1_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'roi_mask'))
        pfi_reg_mask_T1_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'T1', 'reg_mask'))
        pfi_transformation_T1_over_T1 = jph(pfo_tmp, 'trans_{0}_over_{1}_mod_{2}_rigid.txt'.format(
            sj, options['Template_name'], 'T1'))

        assert os.path.exists(pfi_T1_in_sc), pfi_T1_in_sc
        assert os.path.exists(pfi_roi_mask_T1_reoriented), pfi_roi_mask_T1_reoriented
        assert os.path.exists(pfi_reg_mask_T1_reoriented), pfi_reg_mask_T1_reoriented
        assert os.path.exists(pfi_transformation_T1_over_T1), pfi_transformation_T1_over_T1

        pfi_final_roi_mask_T1 = jph(pfo_sc_sj_masks, '{}_roi_mask.nii.gz'.format(sj))  # RESULT
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_T1_in_sc, pfi_roi_mask_T1_reoriented, pfi_transformation_T1_over_T1, pfi_final_roi_mask_T1)
        print_and_run(cmd)

        pfi_final_reg_mask_T1 = jph(pfo_sc_sj_masks, '{0}_{1}_reg_mask.nii.gz'.format(sj, 'T1'))
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_T1_in_sc, pfi_reg_mask_T1_reoriented, pfi_transformation_T1_over_T1, pfi_final_reg_mask_T1)
        print_and_run(cmd)

        del pfi_T1_in_sc, pfi_reg_mask_T1_reoriented, pfi_transformation_T1_over_T1

    if controller['Register_S0']:
        print('Orient header histological S0 and its reg-mask:')
        angles = sj_parameters['angles']
        if isinstance(angles[0], list):
            pitch_theta = -1 * angles[1][1]
        else:
            pitch_theta = -1 * angles[1]

        pfi_original_S0 = jph(pfo_sj_mod, '{0}_{1}.nii.gz'.format(sj, 'S0'))
        assert os.path.exists(pfi_original_S0), pfi_original_S0
        pfi_S0_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}.nii.gz'.format(sj, 'S0'))

        print_and_run('cp {} {}'.format(pfi_original_S0, pfi_S0_reoriented))
        if pitch_theta != 0:
            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_S0_reoriented,
                                           pfi_S0_reoriented,
                                           angle=pitch_theta, principal_axis='pitch')

        pfi_original_reg_mask_S0 = jph(pfo_sj_masks, '{0}_{1}_{2}.nii.gz'.format(sj, 'S0', 'reg_mask'))
        assert os.path.exists(pfi_original_reg_mask_S0), pfi_original_reg_mask_S0
        pfi_reg_mask_S0_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'S0', 'reg_mask'))

        print_and_run('cp {} {}'.format(pfi_original_reg_mask_S0, pfi_reg_mask_S0_reoriented))
        if pitch_theta != 0:
            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_reg_mask_S0_reoriented,
                                           pfi_reg_mask_S0_reoriented,
                                           angle=pitch_theta, principal_axis='pitch')
            del lm

        print('Rigid registration S0:')
        pfi_transformation_S0_over_T1 = jph(pfo_tmp, 'trans_{0}_over_{1}_mod_{2}_rigid.txt'.format(
            sj, options['Template_name'], 'S0'))
        pfi_resampled_S0 = jph(pfo_sc_sj_mod, '{0}_S0.nii.gz'.format(sj))  # RESULT

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(  # Try the non rigid and full mask  -rigOnly
            pfi_mod_reference_atlas, pfi_reg_mask_reference_atlas, pfi_S0_reoriented, pfi_reg_mask_S0_reoriented,
            pfi_transformation_S0_over_T1, pfi_resampled_S0, num_cores_run)

        print_and_run(cmd)

        del angles, pitch_theta, pfi_original_S0, pfi_S0_reoriented, pfi_original_reg_mask_S0, \
            pfi_reg_mask_S0_reoriented, pfi_transformation_S0_over_T1, pfi_resampled_S0, cmd

    if controller['Propagate_S0_related_mods_and_mask']:
        angles = sj_parameters['angles']
        if isinstance(angles[0], list):
            pitch_theta = -1 * angles[1][1]
        else:
            pitch_theta = -1 * angles[1]

        pfi_S0_in_sc = jph(pfo_sc_sj_mod, '{0}_S0.nii.gz'.format(sj))
        pfi_transformation_S0_over_T1 = jph(pfo_tmp, 'trans_{0}_over_{1}_mod_{2}_rigid.txt'.format(
            sj, options['Template_name'], 'S0'))

        for mod in ['FA', 'MD', 'V1']:
            print('Orient header histological {}:'.format(mod))

            pfi_original_MOD = jph(pfo_sj_mod, '{0}_{1}.nii.gz'.format(sj, mod))
            assert os.path.exists(pfi_original_MOD), pfi_original_MOD
            pfi_MOD_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}.nii.gz'.format(sj, mod))

            print_and_run('cp {} {}'.format(pfi_original_MOD, pfi_MOD_reoriented))
            if pitch_theta != 0:
                lt = LABelsToolkit()
                lt.header.apply_small_rotation(pfi_MOD_reoriented, pfi_MOD_reoriented,
                                               angle=pitch_theta, principal_axis='pitch')
                del lt

            print('Resampling {}:'.format(mod))

            pfi_final_MOD= jph(pfo_sc_sj_mod, '{0}_{1}.nii.gz'.format(sj, mod))  # RESULT
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 1'.format(
                pfi_S0_in_sc, pfi_MOD_reoriented, pfi_transformation_S0_over_T1, pfi_final_MOD)
            print_and_run(cmd)

        pfi_reg_mask_S0_reoriented = jph(pfo_tmp, 'histo_header_{0}_{1}_{2}.nii.gz'.format(sj, 'S0', 'reg_mask'))
        assert os.path.exists(pfi_reg_mask_S0_reoriented), pfi_reg_mask_S0_reoriented
        pfi_final_reg_mask_S0_reoriented = jph(pfo_sc_sj_masks, '{0}_{1}_reg_mask.nii.gz'.format(sj, 'S0'))  # RESULT
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_S0_in_sc, pfi_reg_mask_S0_reoriented, pfi_transformation_S0_over_T1, pfi_final_reg_mask_S0_reoriented)
        print_and_run(cmd)

    if controller['Adjustments']:
        # work only on the sc newly generated chart:

        pfi_sc_T1 = jph(pfo_sc_sj_mod, '{0}_T1.nii.gz'.format(sj))
        pfi_sc_S0 = jph(pfo_sc_sj_mod, '{0}_S0.nii.gz'.format(sj))
        pfi_sc_FA = jph(pfo_sc_sj_mod, '{0}_FA.nii.gz'.format(sj))
        pfi_sc_MD = jph(pfo_sc_sj_mod, '{0}_MD.nii.gz'.format(sj))
        pfi_sc_V1 = jph(pfo_sc_sj_mod, '{0}_V1.nii.gz'.format(sj))

        assert os.path.exists(pfi_sc_T1), pfi_sc_T1
        assert os.path.exists(pfi_sc_S0), pfi_sc_S0
        assert os.path.exists(pfi_sc_FA), pfi_sc_FA
        assert os.path.exists(pfi_sc_MD), pfi_sc_MD
        assert os.path.exists(pfi_sc_V1), pfi_sc_V1

        print_and_run('seg_maths {0} -thr 0 {0} '.format(pfi_sc_T1))
        print_and_run('seg_maths {0} -thr 0 {0} '.format(pfi_sc_S0))
        print_and_run('seg_maths {0} -thr 0 {0} '.format(pfi_sc_FA))
        print_and_run('seg_maths {0} -thr 0 {0} '.format(pfi_sc_MD))
        print_and_run('seg_maths {0} -abs   {0} '.format(pfi_sc_V1))

        pfi_sc_roi_mask = jph(pfo_sc_sj_masks, '{}_roi_mask.nii.gz'.format(sj))

        assert os.path.exists(pfi_sc_roi_mask), pfi_sc_roi_mask

        # create mask for V1:
        pfi_V1_mask = jph(pfo_tmp, 'roi_mask_V1_{}.nii.gz'.format(sj))
        stack_a_list_of_images_from_list_pfi(
            [pfi_sc_roi_mask for _ in range(3)], pfi_V1_mask
        )

        print_and_run('seg_maths {0} -mul {1} {0} '.format(pfi_sc_T1, pfi_sc_roi_mask))
        print_and_run('seg_maths {0} -mul {1} {0} '.format(pfi_sc_S0, pfi_sc_roi_mask))
        print_and_run('seg_maths {0} -mul {1} {0} '.format(pfi_sc_FA, pfi_sc_roi_mask))
        print_and_run('seg_maths {0} -mul {1} {0} '.format(pfi_sc_MD, pfi_sc_roi_mask))
        print_and_run('seg_maths {0} -mul {1} {0} '.format(pfi_sc_V1, pfi_V1_mask))


def move_to_stereotaxic_coordinate_from_list(subj_list, controller, options):
    print '\n\n Move to stereotaxic coordinate from list {} \n'.format(subj_list)
    for sj in subj_list:

            move_to_stereotaxic_coordinate_per_subject(sj, controller, options)


if __name__ == '__main__':
    print('process Stereotaxic orientation, local run. ')

    controller_ = {
        'Initialise_sc_folder'               : True,
        'Register_T1'                        : True,
        'Propagate_T1_masks'                 : True,
        'Register_S0'                        : True,
        'Propagate_S0_related_mods_and_mask' : True,
        'Adjustments'                        : True
    }

    options_ = {
        'Template_chart_path': jph(root_atlas, '1305'),
        'Template_name': '1305'}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    # sj_atlas = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    # lsm.input_subjects = sj_atlas

    # lsm.input_subjects = ['0802t1', ]
    # lsm.input_subjects = ['0904t1']
    # lsm.input_subjects = ['1501t1', ]
    lsm.input_subjects = ['13102']
    lsm.update_ls()

    move_to_stereotaxic_coordinate_from_list(lsm.ls, controller_, options_)
