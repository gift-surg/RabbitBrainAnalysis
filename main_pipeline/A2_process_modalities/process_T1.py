"""
T1 processing in their original coordinate system.
"""
import os
from os.path import join as jph
import pickle
import numpy as np

from labels_manager.main import LabelsManager

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_internal_template, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero, orient2std
from tools.auxiliary.utils import print_and_run
from labels_manager.tools.aux_methods.sanity_checks import check_path_validity
from tools.correctors.bias_field_corrector4 import bias_field_correction

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


def process_T1_per_subject(sj, controller):

    print('\nProcessing T1 {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

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

    if controller['orient to standard']:
        print('- orient to standard {}'.format(sj))
        pfi_input_original = jph(pfo_input_sj_3D, sj + '_3D.nii.gz')
        assert check_path_validity(pfi_input_original)
        pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
        orient2std(pfi_input_original, pfi_std)
        del pfi_input_original, pfi_std

    if controller['register roi masks']:
        print('- register roi masks and propagate it {}'.format(sj))

        # --- subject input:
        pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
        assert check_path_validity(pfi_std)

        # --- Get the reference masks from the histologically oriented template ---
        if sj_parameters['category'] in ['ex_vivo', 'op_skull']:
            # This will be the pivotal chart of the template, reoriented respect to the angle in
            # the subjects parameters. (the only utils has to be the subjects parameters.)
            pfi_sj_ref_coord_system = jph(root_internal_template, '1305', 'mod', '1305_T1.nii.gz')
            pfi_reference_roi_mask = jph(root_internal_template, '1305', 'masks', '1305_roi_mask.nii.gz')
        elif sj_parameters['category'] == 'in_vivo':
            pfi_sj_ref_coord_system = jph(root_study_rabbits, 'A_data', 'Utils', '1504t1', '1504t1_T1.nii.gz')
            pfi_reference_roi_mask = jph(root_study_rabbits, 'A_data', 'Utils', '1504t1', '1504t1_roi_mask.nii.gz')
        else:
            raise IOError('ex_vivo, in_vivo or op_skull only.')

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

        lm = LabelsManager()
        lm.header.apply_small_rotation(pfi_sj_ref_coord_system, pfi_sj_ref_coord_system_hd_oriented,
                                       angle=angle_parameter, principal_axis='pitch')
        lm.header.apply_small_rotation(pfi_reference_roi_mask, pfi_reference_roi_mask_hd_oriented,
                                       angle=angle_parameter, principal_axis='pitch')

        # set translational part it its center of mass

        lm.header.modify_translational_part(pfi_sj_ref_coord_system_hd_oriented, pfi_sj_ref_coord_system_hd_oriented,
                                            np.array([0, 0, 0]))
        lm.header.modify_translational_part(pfi_reference_roi_mask_hd_oriented, pfi_reference_roi_mask_hd_oriented,
                                            np.array([0, 0, 0]))

        assert check_path_validity(pfi_sj_ref_coord_system_hd_oriented)
        assert check_path_validity(pfi_reference_roi_mask_hd_oriented)
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_on_' + sj + '.txt')
        pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_on_' + sj + '.nii.gz')
        cmd = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -rigOnly '.format(
            pfi_std,
            pfi_sj_ref_coord_system_hd_oriented,
            pfi_reference_roi_mask_hd_oriented,
            pfi_affine_transformation_ref_on_subject,
            pfi_3d_warped_ref_on_subject,
            num_cores_run)
        print cmd
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

    if controller['adjust mask']:
        print('- adjust mask {}'.format(sj))
        pfi_roi_mask_not_adjusted = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted.nii.gz')
        assert check_path_validity(pfi_roi_mask_not_adjusted)
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')

        dilation_param = sj_parameters['T1_mask_dilation']
        if dilation_param < 0:  # if negative use to erode.
            cmd = 'seg_maths {0} -ero {1} {2}'.format(pfi_roi_mask_not_adjusted,
                                                      -1 * dilation_param,
                                                      pfi_roi_mask)
            print_and_run(cmd)

        elif dilation_param > 0:
            cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask_not_adjusted,
                                                      dilation_param,
                                                      pfi_roi_mask)
            print_and_run(cmd)
        else:
            cmd = 'cp {} {}'.format(pfi_roi_mask_not_adjusted, pfi_roi_mask)
            os.system(cmd)
        del pfi_roi_mask, dilation_param, pfi_roi_mask_not_adjusted

    if controller['cut masks']:
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

    if controller['step bfc']:
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
    elif controller['speed']:
        pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
        assert check_path_validity(pfi_3d_cropped_roi)
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_3d_cropped_roi, pfi_3d_bias_field_corrected)
        print_and_run(cmd)
        del pfi_3d_cropped_roi, pfi_3d_bias_field_corrected, cmd

    if controller['create lesion mask']:
        print('- create lesion mask {}'.format(sj))
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
        del pfi_3d_bias_field_corrected, pfi_roi_mask, pfi_lesion_mask, percentile
    if controller['create reg masks']:
        print('- create reg masks {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        pfi_lesion_mask = jph(pfo_mask, sj + '_T1_lesion_mask.nii.gz')
        assert check_path_validity(pfi_roi_mask)
        assert check_path_validity(pfi_lesion_mask)
        pfi_registration_mask = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
        cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask, pfi_lesion_mask, pfi_registration_mask)
        print_and_run(cmd)
        del pfi_roi_mask, pfi_lesion_mask, pfi_registration_mask, cmd

    if controller['save results']:
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

    controller_steps = {'orient to standard'  : False,
                        'register roi masks'  : True,
                        'adjust mask'         : True,
                        'cut masks'           : True,
                        'step bfc'            : False,
                        'create lesion mask'  : False,
                        'create reg masks'    : False,
                        'save results'        : False,
                        'speed'               : False}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['1505', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    process_T1_from_list(lsm.ls, controller_steps)
