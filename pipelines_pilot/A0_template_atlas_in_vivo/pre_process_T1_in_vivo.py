"""
Align T1 in histological orientation after standard pre-processing.
"""
import os
from os.path import join as jph

from definitions import root_pilot_study
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.utils import print_and_run
from tools.correctors.normalisation import normalise_image_for_the_median
from tools.correctors.coordinates_header_coorectors import from_bicommissural_to_histological_header_orientation


def process_T1(sj, control=None):

    print '\n\n --- Pre process T1 in vivo {} --- \n'.format(sj)

    """ *** PATHS *** """

    pfo_root_main = jph(root_pilot_study, 'A_template_atlas_in_vivo')

    # path to original data
    pfi_3d_nii_original = jph(root_pilot_study, '0_original_data', 'in_vivo', sj, '3D', sj + '_3D.nii.gz')

    if not os.path.isfile(pfi_3d_nii_original):
        msg = 'input file {0} subject {1} does not exists'.format(pfi_3d_nii_original, sj)
        raise IOError(msg)

    # generate_output_folder
    intermediate_outputs_folder = jph(pfo_root_main, sj, 'all_modalities', 'z_pre_process_T1')

    # step_thr
    thr = 300
    pfi_sj_thr = jph(intermediate_outputs_folder, sj + '_thr.nii.gz')

    # step normalisation
    pfi_sj_normalised = jph(intermediate_outputs_folder, sj + '_normalised.nii.gz')

    # step new image creation with the header in histological
    pfi_sj_header_in_histological = jph(intermediate_outputs_folder, sj + '_header_in_histo.nii.gz')

    # Paths to reference oriented in histological coordinates:
    pfi_0802_t1_histo_normalised = jph(pfo_root_main, 'Utils', '0802_t1_histological_orientation',
                                       '0802_t1_reoriented_normalised.nii.gz')
    pfi_0802_t1_histo_roi_mask = jph(pfo_root_main, 'Utils', '0802_t1_histological_orientation',
                                     '0802_t1_reoriented_roi_mask.nii.gz')

    # paths reorientation histological
    pfi_affine_transformation_to_histological = jph(intermediate_outputs_folder, sj + '_aff_to_histological.txt')
    pfi_sj_affine_transformed = jph(intermediate_outputs_folder, sj + '_affine_transformed.nii.gz')

    # path roi mask
    pfi_sj_roi_mask = jph(pfo_root_main, sj, 'masks', sj + '_roi_mask.nii.gz')

    # path subject masked
    pfi_sj_roi_masked = jph(intermediate_outputs_folder, sj + '_roi_masked.nii.gz')

    # path bias field correction
    pfi_sj_bf_corrected = jph(intermediate_outputs_folder, sj + '_bfc.nii.gz')
    # step_bfc
    bfc_tag = '_bfc_default_'

    convergenceThreshold = 0.00001
    maximumNumberOfIterations = (60, 60, 60, 60)  # (70, 70, 70, 70)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 400
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    pri_final_result = jph(pfo_root_main, sj, 'all_modalities', sj + '_T1.nii.gz')
    pri_final_result_masked = jph(pfo_root_main, sj, 'all_modalities', sj + '_T1_masked.nii.gz')

    """ *** PIPELINE *** """

    if control['step_generate_output_folder']:

        cmd = 'mkdir -p ' + intermediate_outputs_folder
        print_and_run(cmd, msg='Create output folder', safety_on=control['safety_on'])

    if control['step_thr']:
        cmd = 'cp {0} {1}; seg_maths {1} -thr 300 {1} '.format(pfi_3d_nii_original, pfi_sj_thr)
        print_and_run(cmd, safety_on=control['safety_on'])

    if control['step_normalise_mean']:
        print('Normalising the image for the mean')
        normalise_image_for_the_median(pfi_sj_thr, pfi_sj_normalised,
                                       exclude_zeros=True,
                                       exclude_zeros_and_negatives=True)

    if control['step_header_in_histological']:
        print('\n Set header in histological orientation:\n')
        from_bicommissural_to_histological_header_orientation(pfi_sj_normalised, pfi_sj_header_in_histological)

    if control['step_reorient_histological']:
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly; '.format(
              pfi_0802_t1_histo_normalised,
              pfi_sj_header_in_histological,
              pfi_affine_transformation_to_histological,
              pfi_sj_affine_transformed)
        print_and_run(cmd, msg='Reorientation', safety_on=control['safety_on'])

    if control['step_copy_histological_mask']:

        cmd = 'mkdir -p ' + jph(pfo_root_main, sj, 'masks')
        print_and_run(cmd, safety_on=control['safety_on'])

        cmd1 = 'cp {0} {1} '.format(pfi_0802_t1_histo_roi_mask, pfi_sj_roi_mask)
        print_and_run(cmd1, safety_on=control['safety_on'])

    if control['step_bfc']:

        print '\nBias field correction: subject {}.\n'.format(sj)

        if not control['safety_on']:
            bias_field_correction(pfi_sj_affine_transformed, pfi_sj_bf_corrected,
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

    if control['step_cut_masks']:
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_sj_bf_corrected, pfi_sj_roi_mask, pfi_sj_roi_masked)
        print_and_run(cmd, safety_on=control['safety_on'])

    if control['step_save_results']:
        cmd = 'cp {0} {1}'.format(pfi_sj_bf_corrected, pri_final_result)
        print_and_run(cmd, safety_on=control['safety_on'])
        cmd = 'cp {0} {1}'.format(pfi_sj_roi_masked, pri_final_result_masked)
        print_and_run(cmd, safety_on=control['safety_on'])

    if control['delete_intermediate_steps']:
        cmd = 'rm -r {0} '.format(intermediate_outputs_folder)
        print_and_run(cmd, msg='Erase pre_process_T1_in_vivo folder for subject ' + sj, safety_on=control['safety_on'])
