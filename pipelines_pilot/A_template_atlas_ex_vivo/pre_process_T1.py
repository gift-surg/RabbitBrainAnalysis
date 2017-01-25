"""
Align T1 in histological orientation after standard pre-processing.
"""
import os
from os.path import join as jph

from definitions import root_pilot_study
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.lesion_mask_extractor import simple_lesion_mask_extractor_path

from tools.auxiliary.path_manipulator import last_two


def process_T1(sj, delete_intermediate_steps=True):

    #################
    # paths manager #
    #################

    root = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

    # path to original data
    path_3d_nii_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, '3D', sj + '_3D.nii.gz')

    if not os.path.isfile(path_3d_nii_original):
        msg = 'input file subject {} does not exists'.format(sj)
        raise IOError(msg)

    # subject 1305 with region of interest (brain + skull) masks:

    s_1305_with_roi = jph(root, 'Utils', '1305_brain_and_skull_mask_T1', '1305_T1.nii.gz')
    s_1305_with_roi_brain_skull_mask = jph(root, 'Utils', '1305_brain_and_skull_mask_T1', '1305_T1_roi_mask.nii.gz')

    # subject 1305 manually oriented in histological coordinates

    s_1305_in_histological_coordinates = jph(root, 'Utils', '1305_histological_orientation', '1305_T1.nii.gz')
    s_1305_in_histological_coordinates_brain_mask = jph(root, 'Utils', '1305_histological_orientation', '1305_T1_roi_mask.nii.gz')

    ####################
    # Controller:      #
    ####################

    safety_on = False
    verbose_on = True

    # --------- #
    step_generate_output_folder = True

    outputs_folder = jph(root, sj, 'all_modalities', 'pre_process_T1')

    # --------- #
    step_reorient              = True

    path_3d_nii_oriented = jph(outputs_folder, sj + '_3D_oriented.nii.gz')

    # --------- #
    step_thr                   = True

    thr = 300
    path_3d_nii_thr = jph(outputs_folder, sj + '_3D_thresholded.nii.gz')

    # --------- # Extract roi
    step_register_masks        = True

    suffix_command_reg_mask = ''
    path_affine_transformation_1305_on_subject = os.path.join(outputs_folder, '1305_on_' + sj + '_3D.txt')
    path_3d_warped_1305_on_subject = os.path.join(outputs_folder, '1305_on_' + sj + '_warped.nii.gz')
    path_resampled_mask_bicommissural = os.path.join(outputs_folder, 'brain_skull_mask_1305_on_' + sj + '.nii.gz')

    # --------- # Cut the roi extracted:
    step_cut_masks             = True

    path_3d_cropped_roi_result = os.path.join(outputs_folder, sj + '_brain_skull_only.nii.gz')

    # --------- # Correct for the bias field
    step_bfc                   = True

    bfc_tag = '_bfc_default_'

    convergenceThreshold = 0.001
    maximumNumberOfIterations = (50, 50, 50, 50)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 200
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    path_3d_bias_field_corrected = jph(outputs_folder, sj + '_bias_field_corrected' + bfc_tag + '.nii.gz')

    # --------- # orient in histological orientation
    step_orient_histological   = True

    suffix_command_reg_histological_coord = ''

    path_3d_nii_histological = jph(outputs_folder, sj + '_histological_coordinates.nii.gz')
    path_roi_mask_histological = jph(outputs_folder, sj + '_roi_mask_histological_coordinates.nii.gz')
    path_affine_transformation_to_histological = jph(outputs_folder, sj + '_transformation_to_histological_coordinates.txt')

    # --------- #  mask of the lesion, to increase robustness registration.
    step_compute_lesion_masks  = True

    path_mask_lesions = jph(outputs_folder, sj + '_lesion_mask.nii.gz')

    # --------- # registration mask is the roi maks minus the lesion masks.
    step_compute_registration_masks = True

    path_registration_mask = jph(outputs_folder, sj + '_registration_mask.nii.gz')

    # --------- # Copy results in the appropriate place in the folder structure
    step_save_results = True

    path_to_T1_final = jph(root, sj, 'all_modalities', sj + '_T1.nii.gz')
    path_to_masks_final = jph(root, sj, 'masks')
    path_to_roi_mask_final = jph(path_to_masks_final, sj + '_roi_mask.nii.gz')
    path_to_lesion_masks_final = jph(path_to_masks_final, sj + '_roi_lesion_mask.nii.gz')
    path_to_registration_masks_final = jph(path_to_masks_final, sj + '_roi_registration_mask.nii.gz')

    # --------- # Save processing in bicommissural orientation, with no resampling errors,
    # will be used for DWI processing.
    step_save_bicommissural = True

    path_to_bicommissural_folder = jph(root, sj, 'bicommissural')
    path_to_T1_bicommissural_final = jph(path_to_bicommissural_folder, sj + '_T1_bicommissural.nii.gz')
    path_to_T1_bicommissural_final_roi_mask = jph(path_to_bicommissural_folder, sj + '_T1_bicommissural_brain_skull_mask.nii.gz')

    # --------- # erase the intermediate results folder
    step_erase_intemediate_results_folder = delete_intermediate_steps

    ##################
    # PIPELINE:      #
    ##################

    """ *** PHASE 1 - INITIAL PROCESSING IN BICOMMISSURAL COORDINATES *** """

    if step_generate_output_folder:

        cmd = 'mkdir -p ' + outputs_folder
        if verbose_on:
            print cmd
        if not safety_on:
            os.system(cmd)

    if step_reorient:

        cmd = ''' cp {0} {1};
                  fslorient -deleteorient {1};
                  fslswapdim {1} -z -y -x {1};
                  fslorient -setqformcode 1 {1};'''.format(path_3d_nii_original, path_3d_nii_oriented)

        if verbose_on:
            print '\nReorient: execution for subject {0}.\n'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)

    if step_thr:

        cmd = 'seg_maths {0} -thr {1} {2}'.format(path_3d_nii_oriented, thr, path_3d_nii_thr)

        if verbose_on:
            print '\nThreshold: execution for subject {0}.\n'.format(sj)
            print 'seg_maths {0} -thr {1} {2}'.format(last_two(path_3d_nii_oriented), thr, last_two(path_3d_nii_thr))

        if not safety_on:
            os.system(cmd)

    if step_register_masks:

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(path_3d_nii_thr,
                                                                       s_1305_with_roi,
                                                                       path_affine_transformation_1305_on_subject,
                                                                       path_3d_warped_1305_on_subject,
                                                                       suffix_command_reg_mask)
        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_3d_nii_thr,
                                                                              s_1305_with_roi_brain_skull_mask,
                                                                              path_affine_transformation_1305_on_subject,
                                                                              path_resampled_mask_bicommissural)
        if verbose_on:
            print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
            print cmd_1
            print cmd_2

        if not safety_on:
            os.system(cmd_1 + cmd_2)

    if step_cut_masks:

        if sj == '1201':
            cmd = 'seg_maths {0} -ero 1 {1}'.format(path_resampled_mask_bicommissural, path_resampled_mask_bicommissural)
            os.system(cmd)

        cmd = 'seg_maths {0} -mul {1} {2}'.format(path_3d_nii_thr, path_resampled_mask_bicommissural, path_3d_cropped_roi_result)

        if verbose_on:
            print '\nCutting newly-created ciccione mask on the subject: subject {0}.\n'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)

    if step_bfc:

        if verbose_on:
            print '\nBias field correction: subject {}.\n'.format(sj)

        if not safety_on:
            bias_field_correction(path_3d_cropped_roi_result, path_3d_bias_field_corrected,
                                  pfi_mask=None,
                                  prefix='',
                                  convergenceThreshold=convergenceThreshold,
                                  maximumNumberOfIterations=maximumNumberOfIterations,
                                  biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                                  wienerFilterNoise=wienerFilterNoise,
                                  numberOfHistogramBins=numberOfHistogramBins,
                                  numberOfControlPoints=numberOfControlPoints,
                                  splineOrder=splineOrder,
                                  print_only=safety_on)

    """ *** PHASE 2 - WE MOVE IN HISTOLOGICAL COORDINATES *** """

    if step_orient_histological:

        cmd0 = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(s_1305_in_histological_coordinates,
                                                                         path_3d_bias_field_corrected,
                                                                         s_1305_in_histological_coordinates_brain_mask,
                                                                         path_resampled_mask_bicommissural,
                                                                         path_affine_transformation_to_histological,
                                                                         path_3d_nii_histological)

        cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(s_1305_in_histological_coordinates,
                                                                            path_resampled_mask_bicommissural,
                                                                            path_affine_transformation_to_histological,
                                                                            path_roi_mask_histological)

        if verbose_on:
            print '\n Alignment in histological coordinates, subject {}.\n'.format(sj)

        if not safety_on:
            os.system(cmd0 + cmd1)

        if verbose_on:
            print '\n Adjust the warped with a threshold to avoid negative {}.\n'.format(sj)
            cmd = 'seg_maths {0} -thr 0 {0}'.format(path_3d_nii_histological)

        if not safety_on:
            os.system(cmd)

    """ *** PHASE 3 - REGISTRATION MASK FOR THE GROUP-WISE REGISTRATION *** """

    if step_compute_lesion_masks:

        if verbose_on:
            print "Lesions masks extractor for subject {} \n".format(sj)

        if not safety_on:
            simple_lesion_mask_extractor_path(im_input_path=path_3d_nii_histological,
                                              im_output_path=path_mask_lesions,
                                              im_mask_foreground_path=path_roi_mask_histological,
                                              safety_on=safety_on)

    if step_compute_registration_masks:

            print "Create registration mask for subject {} \n".format(sj)

            cmd = '''seg_maths {0} -sub {1} {2} '''.format(path_roi_mask_histological, path_mask_lesions, path_registration_mask)
            print cmd

            if not safety_on:
                os.system(cmd)

    """ *** PHASE 4 - DUPLICATE RESULTS IN THE FOLDER STRUCTURE *** """

    if step_save_results:

        cmd = 'mkdir -p {0} '.format(path_to_masks_final)

        cmd0 = 'cp {0} {1}'.format(path_3d_nii_histological, path_to_T1_final)
        cmd1 = 'cp {0} {1}'.format(path_roi_mask_histological, path_to_roi_mask_final)
        cmd2 = 'cp {0} {1}'.format(path_mask_lesions, path_to_lesion_masks_final)
        cmd3 = 'cp {0} {1}'.format(path_registration_mask, path_to_registration_masks_final)

        if verbose_on:
            print 'Saving results'
            print cmd
            print cmd0
            print cmd1
            print cmd2
            print cmd3

        if not safety_on:
            os.system(cmd)
            os.system(cmd0)
            os.system(cmd1)
            os.system(cmd2)
            os.system(cmd3)

    """ *** PHASE 5 - DUPLICATE RESULTS BICOMMISSURAL ORIENTATION AS WELL *** """

    if step_save_bicommissural:

        cmd = 'mkdir -p {0}'.format(path_to_bicommissural_folder)
        cmd0 = 'cp {0} {1}'.format(path_3d_bias_field_corrected, path_to_T1_bicommissural_final)
        cmd1 = 'cp {0} {1}'.format(path_resampled_mask_bicommissural, path_to_T1_bicommissural_final_roi_mask)

        if verbose_on:
            print 'Saving results bicommissural'
            print cmd
            print cmd0
            print cmd1

        if not safety_on:
            os.system(cmd)
            os.system(cmd0)
            os.system(cmd1)

    """ *** PHASE 6 - ERASE INTERMEDIATE RESULTS *** """

    if step_erase_intemediate_results_folder:

        cmd = 'rm -r {0} '.format(outputs_folder)

        if verbose_on:
            print 'Erase pre_process_T1 folder for subject {}.'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)
