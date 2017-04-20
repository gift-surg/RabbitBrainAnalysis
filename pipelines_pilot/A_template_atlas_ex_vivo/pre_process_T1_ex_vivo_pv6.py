"""
Align T1 in histological orientation after standard pre-processing.
"""
import os
from os.path import join as jph
import numpy as np

from definitions import root_pilot_study
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.lesion_mask_extractor import simple_lesion_mask_extractor_path
from tools.auxiliary.utils import print_and_run, adjust_header_from_transformations


def process_T1_pv6(sj, control=None):

    print ' --- Pre process T1 {} --- \n'.format(sj)

    # --- paths manager --- #
    # INPUT:

    pfo_root_main = jph(root_pilot_study, 'A_templ_atlas_ex_vivo')

    # path to original data
    pfi_3d_nii_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, '3D', sj + '_3D.nii.gz')

    if not os.path.isfile(pfi_3d_nii_original):
        msg = 'input file subject {} does not exists'.format(sj)
        raise IOError(msg)

    # subject 1305 with region of interest (brain + skull) masks:
    pfi_1305_bicomm = jph(pfo_root_main, 'Utils', '1305_bicommissural_orientation', '1305_T1_bicomm.nii.gz')
    pfi_1305_bicomm_roi_mask = jph(pfo_root_main, 'Utils', '1305_bicommissural_orientation', '1305_T1_bicomm_roi_mask.nii.gz')

    # subject 1305 manually oriented in histological coordinates

    pfi_1305_in_histological_coordinates = jph(pfo_root_main, 'Utils', '1305_histological_orientation', '1305_T1_histo.nii.gz')
    pfi_1305_in_histological_coordinates_roi_mask = jph(pfo_root_main, 'Utils', '1305_histological_orientation', '1305_T1_histo_roi_mask.nii.gz')

    # check inputs:
    for ph in [pfi_3d_nii_original, pfi_1305_bicomm, pfi_1305_bicomm_roi_mask, pfi_1305_in_histological_coordinates, pfi_1305_in_histological_coordinates_roi_mask]:
        if not os.path.isfile(ph):
            raise IOError('File {} does not exist'.format(ph))

    # --- paths per steps:   --- #

    # generate_output_folder
    outputs_folder = jph(pfo_root_main, sj, 'all_modalities', 'z_pre_process_T1')

    # step_reorient
    pfi_3d_nii_oriented = jph(outputs_folder, sj + '_3D_oriented.nii.gz')

    # step_thr
    thr = 300
    pfi_3d_nii_thr = jph(outputs_folder, sj + '_3D_thresholded.nii.gz')

    # step_register_masks
    suffix_command_reg_mask = ''
    pfi_affine_transformation_1305_on_subject = os.path.join(outputs_folder, '1305_on_' + sj + '_3D.txt')
    pfi_3d_warped_1305_on_subject = os.path.join(outputs_folder, '1305_on_' + sj + '_warped.nii.gz')
    pfi_resampled_mask_bicomm = os.path.join(outputs_folder, 'brain_skull_mask_1305_on_' + sj + '.nii.gz')

    # step_cut_masks
    pfi_3d_cropped_roi = os.path.join(outputs_folder, sj + '_brain_skull_only.nii.gz')

    # step_bfc
    bfc_tag = '_bfc_default_'

    convergenceThreshold = 0.001
    maximumNumberOfIterations = (50, 50, 50, 50)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 200
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    pfi_3d_bias_field_corrected = jph(outputs_folder, sj + '_bias_field_corrected' + bfc_tag + '.nii.gz')

    # step_orient_histological
    pfi_3d_histological = jph(outputs_folder, sj + '_histological_coordinates.nii.gz')
    pfi_roi_mask_histological = jph(outputs_folder, sj + '_roi_mask_histological_coordinates.nii.gz')
    pfi_affine_transformation_to_histological = jph(outputs_folder,
                                                     sj + '_transformation_to_histological_coordinates.txt')

    # step_compute_lesion_masks
    pfo_mask_lesions = jph(outputs_folder, sj + '_lesion_mask.nii.gz')

    # step_compute_reg_masks
    pfi_registration_mask = jph(outputs_folder, sj + '_registration_mask.nii.gz')

    # step_copy_results
    pfi_T1_final = jph(pfo_root_main, sj, 'all_modalities', sj + '_T1.nii.gz')
    pfo_masks_final = jph(pfo_root_main, sj, 'masks')
    pfi_roi_mask_final = jph(pfo_masks_final, sj + '_roi_mask.nii.gz')
    pfi_lesion_masks_final = jph(pfo_masks_final, sj + '_roi_lesion_mask.nii.gz')
    pfi_registration_masks_final = jph(pfo_masks_final, sj + '_roi_registration_mask.nii.gz')

    # step_save_bicommissural
    pfo_bicommissural = jph(pfo_root_main, sj, 'bicommissural')
    pfi_T1_bicommissural_final = jph(pfo_bicommissural, sj + '_T1_bicommissural.nii.gz')
    pfi_T1_bicommissural_final_roi_mask = jph(pfo_bicommissural,
                                                  sj + '_T1_bicommissural_brain_skull_mask.nii.gz')

    """ *** PHASE 1 - INITIAL PROCESSING IN BICOMMISSURAL COORDINATES *** """

    if control['step_generate_output_folder']:

        cmd = 'mkdir -p ' + outputs_folder
        print_and_run(cmd, msg='Create output folder', safety_on=control['safety_on'])

    if control['step_reorient']:

        cmd = ''' cp {0} {1};
                  fslorient -deleteorient {1};
                  fslswapdim {1} -z -y -x {1};
                  fslorient -setqformcode 1 {1};'''.format(pfi_3d_nii_original, pfi_3d_nii_oriented)
        print_and_run(cmd, msg='Reorient: execution for subject {0}.'.format(sj), safety_on=control['safety_on'])

    if control['step_thr']:

        cmd = 'seg_maths {0} -thr {1} {2}'.format(pfi_3d_nii_oriented, thr, pfi_3d_nii_thr)

        print_and_run(cmd, msg='Thresholding ' + sj, safety_on=control['safety_on'])

    if control['step_register_masks']:

        cmd0 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(
               pfi_3d_nii_thr,
               pfi_1305_bicomm,
               pfi_affine_transformation_1305_on_subject,
               pfi_3d_warped_1305_on_subject,
               suffix_command_reg_mask)
        cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_3d_nii_thr,
                pfi_1305_bicomm_roi_mask,
                pfi_affine_transformation_1305_on_subject,
                pfi_resampled_mask_bicomm)

        print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])

    if control['step_cut_masks']:

        if sj == '1201':
            cmd = 'seg_maths {0} -ero 1 {1}'.format(pfi_resampled_mask_bicomm, pfi_resampled_mask_bicomm)
            print_and_run(cmd, safety_on=control['safety_on'])

        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_3d_nii_thr, pfi_resampled_mask_bicomm,
                                                  pfi_3d_cropped_roi)

        print '\nCutting newly-created ciccione mask on the subject: subject {0}.\n'.format(sj)
        print_and_run(cmd, safety_on=control['safety_on'])

    if control['step_bfc']:

        print '\nBias field correction: subject {}.\n'.format(sj)

        if not control['safety_on']:
            bias_field_correction(pfi_3d_cropped_roi, pfi_3d_bias_field_corrected,
                                  pfi_mask=None,
                                  prefix='',
                                  convergenceThreshold=convergenceThreshold,
                                  maximumNumberOfIterations=maximumNumberOfIterations,
                                  biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                                  wienerFilterNoise=wienerFilterNoise,
                                  numberOfHistogramBins=numberOfHistogramBins,
                                  numberOfControlPoints=numberOfControlPoints,
                                  splineOrder=splineOrder,
                                  print_only=control['safety_on'])

    """ *** PHASE 2 - WE MOVE IN HISTOLOGICAL COORDINATES *** """

    if control['step_orient_histological']:

        if not control['safety_on']:

            if sj == '1805' or sj == '2002' or sj == '2502':
                pass
            else:
                theta = -np.pi / float(3)

                adjust_header_from_transformations(pfi_3d_bias_field_corrected, pfi_3d_bias_field_corrected,
                                                   theta=-theta, trasl=(0, 0, 0))
                adjust_header_from_transformations(pfi_resampled_mask_bicomm, pfi_resampled_mask_bicomm,
                                                   theta=theta, trasl=(0, 0, 0))

        # cmd0 = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(
        #          pfi_1305_in_histological_coordinates,
        #          pfi_3d_bias_field_corrected,
        #          pfi_1305_in_histological_coordinates_roi_mask,
        #          pfi_resampled_mask_bicomm,
        #          pfi_affine_transformation_to_histological,
        #          pfi_3d_histological)

        cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_1305_in_histological_coordinates,
                pfi_resampled_mask_bicomm,
                pfi_affine_transformation_to_histological,
                pfi_roi_mask_histological)

        print '\n Alignment in histological coordinates, subject {}.\n'.format(sj)
        # print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])

        cmd = 'seg_maths {0} -thr 0 {0}'.format(pfi_3d_histological)
        print_and_run(cmd, msg='threshold the warped ' + sj, safety_on=control['safety_on'])

    """ *** PHASE 3 - REGISTRATION MASK FOR THE GROUP-WISE REGISTRATION *** """

    if control['step_compute_lesion_masks']:

        print "Lesions masks extractor for subject {} \n".format(sj)

        if not control['safety_on']:
            simple_lesion_mask_extractor_path(im_input_path=pfi_3d_histological,
                                              im_output_path=pfo_mask_lesions,
                                              im_mask_foreground_path=pfi_roi_mask_histological,
                                              safety_on=control['safety_on'])
    if control['step_compute_reg_masks']:

            cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask_histological, pfo_mask_lesions,
                                                       pfi_registration_mask)  # until here seems correct.
            print_and_run(cmd, msg='Create registration mask ' + sj, safety_on=control['safety_on'])

    """ *** PHASE 4 - DUPLICATE RESULTS IN THE FOLDER STRUCTURE *** """

    if control['step_save_results']:

        cmd = 'mkdir -p {0} '.format(pfo_masks_final)

        cmd0 = 'cp {0} {1}'.format(pfi_3d_histological, pfi_T1_final)
        cmd1 = 'cp {0} {1}'.format(pfi_roi_mask_histological, pfi_roi_mask_final)
        cmd2 = 'cp {0} {1}'.format(pfo_mask_lesions, pfi_lesion_masks_final)
        cmd3 = 'cp {0} {1}'.format(pfi_registration_mask, pfi_registration_masks_final)

        print 'Saving results ' + sj
        print_and_run(cmd,  safety_on=control['safety_on'])
        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])
        print_and_run(cmd3, safety_on=control['safety_on'])

    """ *** PHASE 5 - DUPLICATE RESULTS BICOMMISSURAL ORIENTATION AS WELL *** """

    if control['step_save_bicommissural']:

        cmd = 'mkdir -p {0}'.format(pfo_bicommissural)
        cmd0 = 'cp {0} {1}'.format(pfi_3d_bias_field_corrected, pfi_T1_bicommissural_final)
        cmd1 = 'cp {0} {1}'.format(pfi_resampled_mask_bicomm, pfi_T1_bicommissural_final_roi_mask)

        print 'Saving results bicommissural'
        print_and_run(cmd, safety_on=control['safety_on'])
        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])

    """ *** PHASE 6 - ERASE INTERMEDIATE RESULTS *** """

    if control['delete_intermediate_steps']:

        cmd = 'rm -r {0} '.format(outputs_folder)
        print_and_run(cmd, msg='Erase pre_process_T1 folder for subject ' + sj, safety_on=control['safety_on'])
