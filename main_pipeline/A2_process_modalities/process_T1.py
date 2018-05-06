import os
from os.path import join as jph
import pickle
import numpy as np
import nibabel as nib

from LABelsToolkit.main import LABelsToolkit
from LABelsToolkit.tools.aux_methods.utils_nib import set_new_data
from LABelsToolkit.tools.image_colors_manipulations.relabeller import relabeller
from LABelsToolkit.tools.aux_methods.sanity_checks import check_path_validity

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_atlas, num_cores_run, multi_atlas_subjects
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero, orient2std
from tools.auxiliary.utils import print_and_run
from tools.correctors.bias_field_corrector4 import bias_field_correction
from main_pipeline.A0_main.subject_parameters_manager import get_list_names_subjects_in_atlas

from LABelsToolkit.tools.visualiser.see_volume import see_array
from LABelsToolkit.tools.detections.get_segmentation import MoG

"""
Processing list for each T1 of each subject:
(there are artefacts shared by multiple modalities, the group subdivision is meaningless. It must be done
subject-wise, using the map of parameters under U_Utils/maps)

Generate intermediate folder
Generate output folder
Orient to standard - fsl
Get mask - subject params.
Cut mask
Bias field correction
Compute registration and lesion mask
"""


def process_T1_per_subject(sj, step):

    print('\nProcessing T1 {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    options = sj_parameters['options_T1']

    pfo_input_sj_3D = jph(root_study_rabbits, '01_nifti', study, category, sj, sj + '_3D')
    pfo_output_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    # input sanity check:
    if not os.path.exists(pfo_input_sj_3D):
        raise IOError('Input folder T1 does not exist. {}'.format(pfo_input_sj_3D))

    # --  Generate intermediate and output folder
    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'masks')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_T1')

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    if step['orient_to_standard']:
        print('- orient to standard {}'.format(sj))
        pfi_input_original = jph(pfo_input_sj_3D, sj + '_3D.nii.gz')
        assert check_path_validity(pfi_input_original)
        pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
        orient2std(pfi_input_original, pfi_std)
        del pfi_input_original, pfi_std

    if step['create_roi_masks']:

        if options['roi_mask'] == 'pivotal' or options['roi_mask'] in multi_atlas_subjects:
            print('- register roi masks and propagate it with representative {} on {}'.format(options['roi_mask'], sj))

            if options['roi_mask'] == 'pivotal':
                if sj_parameters['category'] in ['ex_vivo', 'op_skull']:
                    reference_subject = '1305'
                elif sj_parameters['category'] == 'in_vivo':
                    reference_subject = '1504t1'
                else:
                    raise IOError('ex_vivo, in_vivo or op_skull only.')

            else:
                reference_subject = options['roi_mask']

            # --- subject input:
            pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
            assert check_path_validity(pfi_std)

            # --- Get the reference masks from the histologically oriented template ---
           # reference subject:
            pfi_sj_ref_coord_system = jph(root_atlas, reference_subject, 'mod', '{}_T1.nii.gz'.format(reference_subject))
            # original mask
            pfi_reference_roi_mask = jph(root_atlas, reference_subject, 'masks', '{}_roi_mask.nii.gz'.format(reference_subject))

            assert check_path_validity(pfi_sj_ref_coord_system)
            assert check_path_validity(pfi_reference_roi_mask)

            # --- Get the angle difference from histological (template) to bicommissural (data) and orient header ---
            if isinstance(sj_parameters['angles'][0], list):
                angles = sj_parameters['angles'][0]
            else:
                angles = sj_parameters['angles']

            angle_parameter = angles[1]

            pfi_sj_ref_coord_system_hd_oriented = jph(pfo_tmp, 'reference_for_mask_registration.nii.gz')
            pfi_reference_roi_mask_hd_oriented = jph(pfo_tmp, 'reference_for_mask_registration_mask.nii.gz')

            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_sj_ref_coord_system, pfi_sj_ref_coord_system_hd_oriented,
                                           angle=angle_parameter, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_reference_roi_mask, pfi_reference_roi_mask_hd_oriented,
                                           angle=angle_parameter, principal_axis='pitch')

            # set translational part to zero

            lm.header.modify_translational_part(pfi_sj_ref_coord_system_hd_oriented, pfi_sj_ref_coord_system_hd_oriented,
                                                np.array([0, 0, 0]))
            lm.header.modify_translational_part(pfi_reference_roi_mask_hd_oriented, pfi_reference_roi_mask_hd_oriented,
                                                np.array([0, 0, 0]))

            assert check_path_validity(pfi_sj_ref_coord_system_hd_oriented)
            assert check_path_validity(pfi_reference_roi_mask_hd_oriented)
            pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_on_' + sj + '.txt')
            pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_on_' + sj + '.nii.gz')
            cmd = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -speeeeed '.format(  # -rigOnly
                pfi_std,
                pfi_sj_ref_coord_system_hd_oriented,
                pfi_reference_roi_mask_hd_oriented,
                pfi_affine_transformation_ref_on_subject,
                pfi_3d_warped_ref_on_subject,
                num_cores_run)
            print_and_run(cmd)

            print('- propagate roi masks {}'.format(sj))

            assert check_path_validity(pfi_affine_transformation_ref_on_subject)
            pfi_roi_mask_not_adjusted = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted.nii.gz')
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_std,
                pfi_reference_roi_mask_hd_oriented,
                pfi_affine_transformation_ref_on_subject,
                pfi_roi_mask_not_adjusted)
            print_and_run(cmd)
            del pfi_std, pfi_sj_ref_coord_system, pfi_reference_roi_mask, \
                angle_parameter, angles, pfi_sj_ref_coord_system_hd_oriented, pfi_reference_roi_mask_hd_oriented,\
                pfi_affine_transformation_ref_on_subject, pfi_3d_warped_ref_on_subject, pfi_roi_mask_not_adjusted, cmd

        elif options['roi_mask'] == 'slim':
            # Robust roi extraction - uses the binarised brain tissue for the partial skull stripping.
            # This should be modified to get the slim registration, otherwise is an overkill
            print('- register roi masks and propagate brain_tissue masks from each subject of the multi-atlas on {}'.format(sj))

            # --- subject input:
            pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
            assert check_path_validity(pfi_std)

            list_names_subjects_in_atlas = get_list_names_subjects_in_atlas(pfo_subjects_parameters)
            list_brain_mask_registered_on_target = []
            for atlas_sj in list_names_subjects_in_atlas:

                pfi_sj_ref_coord_system = jph(root_atlas, atlas_sj, 'mod', '{}_T1.nii.gz'.format(atlas_sj))
                pfi_reference_brain_tissue = jph(root_atlas, atlas_sj, 'masks', '{}_brain_tissue.nii.gz'.format(atlas_sj))
                pfi_reference_reg_mask = jph(root_atlas, atlas_sj, 'masks', '{}_reg_mask.nii.gz'.format(atlas_sj))

                assert check_path_validity(pfi_sj_ref_coord_system)
                assert check_path_validity(pfi_reference_brain_tissue)
                assert check_path_validity(pfi_reference_reg_mask)

                # --- Get the angle difference from histological (template) to bicommissural (data) and orient header ---
                if isinstance(sj_parameters['angles'][0], list):
                    angles = sj_parameters['angles'][0]
                else:
                    angles = sj_parameters['angles']

                angle_parameter = angles[1]

                pfi_sj_ref_coord_system_hd_oriented = jph(pfo_tmp, 'reference_for_T1_hd_oriented.nii.gz')
                pfi_reference_brain_tissue_hd_oriented = jph(pfo_tmp, 'reference_for_brain_tissue_hd_oriented.nii.gz')
                pfi_reference_reg_mask_hd_oriented = jph(pfo_tmp, 'reference_for_reg_mask_hd_oriented.nii.gz')

                lm = LABelsToolkit()
                lm.header.apply_small_rotation(pfi_sj_ref_coord_system, pfi_sj_ref_coord_system_hd_oriented,
                                               angle=angle_parameter, principal_axis='pitch')
                lm.header.apply_small_rotation(pfi_reference_brain_tissue, pfi_reference_brain_tissue_hd_oriented,
                                               angle=angle_parameter, principal_axis='pitch')
                lm.header.apply_small_rotation(pfi_reference_reg_mask, pfi_reference_reg_mask_hd_oriented,
                                               angle=angle_parameter, principal_axis='pitch')

                # set translational part to zero
                lm.header.modify_translational_part(pfi_sj_ref_coord_system_hd_oriented, pfi_sj_ref_coord_system_hd_oriented,
                                                    np.array([0, 0, 0]))
                lm.header.modify_translational_part(pfi_reference_brain_tissue_hd_oriented, pfi_reference_brain_tissue_hd_oriented,
                                                    np.array([0, 0, 0]))
                lm.header.modify_translational_part(pfi_reference_reg_mask_hd_oriented, pfi_reference_reg_mask_hd_oriented,
                                                    np.array([0, 0, 0]))

                # get the registration mask as reg_mask and brain tissue product:
                pfi_reg_mask_times_brain_tissue_affine_for_sj = jph(pfo_tmp, 'reference_for_roi_mask_times_brain_tissue_hd_oriented.nii.gz')
                cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_reference_brain_tissue_hd_oriented,
                                                          pfi_reference_reg_mask_hd_oriented,
                                                          pfi_reg_mask_times_brain_tissue_affine_for_sj)
                print_and_run(cmd)

                pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_{0}_on_{1}.txt'.format(atlas_sj, sj))
                pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_{0}_on_{1}.nii.gz'.format(atlas_sj, sj))
                cmd = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -speeeeed '.format(
                    pfi_std,
                    pfi_sj_ref_coord_system_hd_oriented,
                    pfi_reg_mask_times_brain_tissue_affine_for_sj,
                    pfi_affine_transformation_ref_on_subject,
                    pfi_3d_warped_ref_on_subject,
                    num_cores_run)
                print cmd
                print_and_run(cmd)

                print('- propagate roi masks {}'.format(sj))

                assert check_path_validity(pfi_affine_transformation_ref_on_subject)
                pfi_brain_tissue_from_multi_atlas_sj = \
                    jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, atlas_sj))
                cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                    pfi_std,
                    pfi_reference_brain_tissue_hd_oriented,
                    pfi_affine_transformation_ref_on_subject,
                    pfi_brain_tissue_from_multi_atlas_sj)
                print_and_run(cmd)

                list_brain_mask_registered_on_target.append(pfi_brain_tissue_from_multi_atlas_sj)

            # label fusion MV of the region of interest for the final region of interest:

            # create the stack of the registered roi masks:
            pfi_stack_roi_mask = jph(pfo_tmp, '{0}_T1_roi_masks_from_atlases_stack.nii.gz'.format(sj))
            lt = LABelsToolkit()
            lt.manipulate_shape.stack_list_pfi_images(list_brain_mask_registered_on_target, pfi_stack_roi_mask)

            # get output from the stack:
            cmd = 'seg_maths {0}  -merge {1} {2} '.format(
                jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, list_names_subjects_in_atlas[0])),
                len(list_names_subjects_in_atlas) - 1,
                4
            )
            for p in list_names_subjects_in_atlas[1:]:
                cmd += ' {} '.format(jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, p)))
            cmd += ' {} '.format(pfi_stack_roi_mask)
            print_and_run(cmd)

            # merge the roi masks in one:
            pfi_roi_mask_not_adjusted_multi = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted_MV.nii.gz')
            cmd = 'seg_LabFusion  -in {0} -out {1} -MV '.format(pfi_stack_roi_mask, pfi_roi_mask_not_adjusted_multi)
            print_and_run(cmd)

    if step['adjust_mask']:
        print('- adjust mask {}'.format(sj))
        pfi_roi_mask_not_adjusted = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted_MV.nii.gz')
        if not os.path.exists(pfi_roi_mask_not_adjusted):
            pfi_roi_mask_not_adjusted = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted.nii.gz')

        assert check_path_validity(pfi_roi_mask_not_adjusted)
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')

        dilation_param = sj_parameters['T1_mask_dilation']
        if dilation_param < 0:  # if negative use to erode.
            cmd = 'seg_maths {0} -ero {1} {2}'.format(pfi_roi_mask_not_adjusted,
                                                      -1 * dilation_param,
                                                      pfi_roi_mask)
        elif dilation_param > 0:
            cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask_not_adjusted,
                                                      dilation_param,
                                                      pfi_roi_mask)
        else:
            cmd = 'cp {} {}'.format(pfi_roi_mask_not_adjusted, pfi_roi_mask)
        print_and_run(cmd)
        del pfi_roi_mask, dilation_param, pfi_roi_mask_not_adjusted, cmd

    if step['cut_masks']:
        if options['crop_roi']:
            print('- cut masks {}'.format(sj))
            pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
            pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
            assert check_path_validity(pfi_std)
            assert check_path_validity(pfi_roi_mask)
            pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
            cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_std, pfi_roi_mask, pfi_3d_cropped_roi)
            print '\nCutting newly-created ciccione mask on the subject: subject {0}.\n'.format(sj)
            print_and_run(cmd)
            del pfi_std, pfi_roi_mask, pfi_3d_cropped_roi, cmd
        else:
            pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
            assert check_path_validity(pfi_std)
            pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
            cmd = 'cp {0} {1}'.format(pfi_std, pfi_3d_cropped_roi)
            print_and_run(cmd)

    if step['step_bfc']:
        print('- step bfc {}'.format(sj))
        pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
        assert check_path_validity(pfi_3d_cropped_roi)
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        bfc_param = sj_parameters['bias_field_parameters']
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        bias_field_correction(pfi_3d_cropped_roi, pfi_3d_bias_field_corrected,
                              pfi_mask=pfi_roi_mask,
                              prefix='',
                              convergenceThreshold=bfc_param[0],
                              maximumNumberOfIterations=bfc_param[1],
                              biasFieldFullWidthAtHalfMaximum=bfc_param[2],
                              wienerFilterNoise=bfc_param[3],
                              numberOfHistogramBins=bfc_param[4],
                              numberOfControlPoints=bfc_param[5],
                              splineOrder=bfc_param[6],
                              print_only=False)

        del pfi_3d_cropped_roi, pfi_3d_bias_field_corrected, bfc_param, pfi_roi_mask

    if step['create_reg_mask']:

        if options['reg_mask'] == 0:
            print('remove percentiles, values added manually:')
            pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
            pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
            assert check_path_validity(pfi_3d_bias_field_corrected)
            assert check_path_validity(pfi_roi_mask)
            pfi_lesion_mask = jph(pfo_mask, sj + '_T1_lesion_mask.nii.gz')
            percentile = sj_parameters['T1_window_percentile']
            percentile_lesion_mask_extractor(im_input_path=pfi_3d_bias_field_corrected,
                                             im_output_path=pfi_lesion_mask,
                                             im_mask_foreground_path=pfi_roi_mask,
                                             percentiles=percentile,
                                             safety_on=False)

            # final tuning:
            pfi_registration_mask = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
            cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask, pfi_lesion_mask, pfi_registration_mask)
            print_and_run(cmd)
            del pfi_roi_mask, pfi_lesion_mask, pfi_registration_mask, cmd

        elif options['reg_mask'] > 0:
            K = options['reg_mask']
            print('remove the first (not background) and the last gaussians after MoG fitting, with K = {}.'.format(K))
            pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
            pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
            assert os.path.exists(pfi_3d_bias_field_corrected)
            assert check_path_validity(pfi_roi_mask)
            pfi_mog_segm = jph(pfo_tmp, '{}_mog_segm.nii.gz'.format(sj))
            T1_bfc = nib.load(pfi_3d_bias_field_corrected)
            roi_mask = nib.load(pfi_roi_mask)
            c, p = MoG(T1_bfc, K=5, pre_process_median_filter=True, mask_im=roi_mask, pre_process_only_interquartile=True)
            nib.save(c, '/Users/sebastiano/Desktop/zzz.nii.gz')
            old_labels = list(range(K))  # [0, 1, 2, 3, 4]
            new_labels = [1, ] * len(old_labels)
            new_labels[0], new_labels[1], new_labels[-1] = 0, 0, 0  # [0, 0, 1, ..., 1, 0]
            im_crisp = set_new_data(c, np.copy(relabeller(c.get_data(), old_labels, new_labels)), new_dtype=np.uint8)
            nib.save(im_crisp, pfi_mog_segm)

            # final tuning:
            pfi_registration_mask = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
            cmd0 = 'seg_maths {0} -ero 3 {1}'.format(pfi_mog_segm, pfi_registration_mask)
            cmd1 = 'seg_maths {0} -fill {0}'.format(pfi_registration_mask)
            cmd2 = 'seg_maths {0} -dil 3 {0}'.format(pfi_registration_mask)
            cmd3 = 'seg_maths {0} -fill {0}'.format(pfi_registration_mask)

            print_and_run(cmd0)
            print_and_run(cmd1)
            print_and_run(cmd2)
            print_and_run(cmd3)

            del pfi_3d_bias_field_corrected, p, c, T1_bfc, pfi_registration_mask, cmd0, cmd1, cmd2, cmd3

    if step['save_results']:
        print('- save results {}'.format(sj))
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        assert check_path_validity(pfi_3d_bias_field_corrected)
        pfi_3d_final_destination = jph(pfo_mod, sj + '_T1.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_3d_bias_field_corrected, pfi_3d_final_destination)
        print_and_run(cmd)
        del pfi_3d_bias_field_corrected, pfi_3d_final_destination, cmd


def process_T1_from_list(subj_list, controller):

    print '\n\n Processing T1 subjects from list {} \n'.format(subj_list)
    for sj in subj_list:

        process_T1_per_subject(sj, controller)


if __name__ == '__main__':
    print('process T1, local run. ')

    controller_steps = {'orient_to_standard'       : False,
                        'create_roi_masks'         : False,
                        'adjust_mask'              : False,
                        'cut_masks'                : False,
                        'step_bfc'                 : False,
                        'create_reg_mask'          : True,
                        'save_results'             : False}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['4901']
    lsm.update_ls()

    process_T1_from_list(lsm.ls, controller_steps)
