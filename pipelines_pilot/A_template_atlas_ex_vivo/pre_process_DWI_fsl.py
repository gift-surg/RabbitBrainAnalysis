"""
Process and align DWI in histological orientation.  https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/UsersGuide
"""
import os
from os.path import join as jph
import nibabel as nib

from definitions import root_pilot_study
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data, \
    reproduce_slice_fourth_dimension_path
from tools.auxiliary.utils import print_and_run
from tools.parsers.parse_bruker_txt import parse_bruker_dwi_txt
from tools.correctors.slope_corrector import slope_corrector_path


def process_DWI_fsl(sj, control=None):

    print ' --- Pre process DWI FSL {} --- \n'.format(sj)

    # --- paths manager, general --- #

    root = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

    # path to DWI data subject

    pfi_dwi_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.nii.gz')
    pfi_dwi_txt_data_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.txt')

    if not os.path.isfile(pfi_dwi_original):
        msg = 'Input file subject {} does not exists'.format(sj)
        raise IOError(msg)

    if not os.path.isfile(pfi_dwi_txt_data_original):
        msg = 'Input data dfile subject {} does not exists'.format(sj)
        raise IOError(msg)

    # subject 1305 with region of interest (brain + skull) masks - to extract the regions of interests:

    s_1305_with_roi = jph(root, 'Utils', '1305_brain_and_skull_mask_T1_dwi_oriented', '1305_T1.nii.gz')
    s_1305_with_roi_brain_skull_mask = jph(root, 'Utils', '1305_brain_and_skull_mask_T1_dwi_oriented',
                                           '1305_T1_roi_mask.nii.gz')

    # --- Paths per step:  --- #

    # Paths to T1 images and roi mask of the same subject in histological coordinates:
    T1_in_histological_coordinates = jph(root, sj, 'all_modalities', sj + '_T1.nii.gz')
    T1_in_histological_coordinates_brain_mask = jph(root, sj, 'masks', sj + '_roi_mask.nii.gz')

    # generate_output_folder
    outputs_folder = jph(root, sj, 'all_modalities', 'z_pre_process_DWI_fsl')

    # step_squeeze  in case the timepoints are in the 5th rather than the fourth dim
    pfi_dwi_squeezed = jph(outputs_folder, sj + '_DWI_squeezed.nii.gz')

    # step_extract_bval_bvect_slope
    # Output filenames (fn) are the default: 'DwDir.txt', 'DwEffBval.txt', 'DwGradVec.txt', 'VisuCoreDataSlope.txt'
    pfi_input_bvals   = os.path.join(outputs_folder, sj + '_DwEffBval.txt')
    pfi_input_bvects  = os.path.join(outputs_folder, sj + '_DwGradVec.txt')
    pfi_slopes_txt_file = jph(outputs_folder, sj + '_VisuCoreDataSlope.txt')

    # step_extract_first_timepoint
    pfi_dwi_b0 = jph(outputs_folder, sj + '_DWI_first_timepoint.nii.gz')

    # step_grab_the_roi_mask
    pfi_affine_transformation_1305_bicom_on_b0 = jph(outputs_folder, sj + '_affine_transf_1305_bicom_on_b0.txt')
    pfi_warped_1305_bicom_on_b0 = jph(outputs_folder, sj + '_warped_1305_bicom_on_b0.nii.gz')
    suffix_command_reg_1305_bicom_on_b0 = ''
    pfi_roi_mask = jph(outputs_folder, sj + '_roi_mask.nii.gz')

    # step_dilate_mask
    dil_factor = 0
    pfi_roi_mask_dilated = jph(outputs_folder, sj + '_roi_mask_dilated.nii.gz')

    # step_cut_to_mask_dwi
    pfi_dwi_cropped_to_roi = jph(outputs_folder, sj + '_DWI_roi_cropped.nii.gz')

    # step_correct_the_slope
    pfi_dwi_slope_corrected = jph(outputs_folder, sj + '_DWI_slope_corrected.nii.gz')

    # step_eddy_current_corrections
    prefix_dwi_eddy_corrected = sj + '_DWI_fsl_eddy_corrected'
    pfi_dwi_eddy_corrected    = jph(outputs_folder, prefix_dwi_eddy_corrected + '.nii.gz')

    # step_dwi_analysis_with_fsl
    prefix_fsl_output = 'fsl_dtifit_'
    name_for_analysis_fsl = prefix_fsl_output + sj
    pfi_analysis_fsl = jph(outputs_folder, name_for_analysis_fsl)

    suffix_results_to_keep = ['FA', 'MD', 'V1', 'S0']
    fn_results_to_keep = [name_for_analysis_fsl + '_' + pref + '.nii.gz' for pref in suffix_results_to_keep]

    # step_orient_directions  FSL reorientation
    pfi_mask_reoriented = jph(outputs_folder, sj + '_roi_mask_dilated_oriented.nii.gz')
    pfi_mask_reoriented_V1 = jph(outputs_folder, sj + '_roi_mask_dilated_oriented_V1.nii.gz')
    pfi_mask_reoriented_tensor = jph(outputs_folder, sj + '_roi_mask_dilated_oriented_tensor.nii.gz')

    # step_orient_histological
    pfi_affine_transformation_to_histological = jph(outputs_folder, sj + '_transf_to_histological.txt')
    pfi_mask_histological = jph(outputs_folder, 'histo_' + sj + '_DWI_mask.nii.gz')
    prefix_histo = 'histo_'

    # step_bfc_b0
    convergenceThreshold = 0.001
    maximumNumberOfIterations = (50, 50, 50, 50)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 200
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    """ *** PHASE 1 - DWI PRE-PROCESSING IN BICOMMISSURAL COORDINATES *** """

    if control['step_generate_output_folder']:

        cmd = 'mkdir -p ' + outputs_folder
        print_and_run(cmd, msg='Generate output folder', safety_on=control['safety_on'])

    if control['step_squeeze']:

        print '\n Squeeze for DWI images: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            squeeze_image_from_path(pfi_dwi_original, pfi_dwi_squeezed, copy_anyway=True)

    if control['step_extract_bval_bvect_slope']:

        print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            parse_bruker_dwi_txt(pfi_dwi_txt_data_original,
                                 output_folder=outputs_folder,
                                 prefix=sj + '_')

    if control['step_extract_first_timepoint']:

        print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not control['safety_on']:
            nib_dwi = nib.load(pfi_dwi_squeezed)
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, pfi_dwi_b0)

    if control['step_grab_the_roi_mask']:

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(pfi_dwi_b0,
                                                                       s_1305_with_roi,
                                                                       pfi_affine_transformation_1305_bicom_on_b0,
                                                                       pfi_warped_1305_bicom_on_b0,
                                                                       suffix_command_reg_1305_bicom_on_b0)
        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(pfi_dwi_b0,
                                                                          s_1305_with_roi_brain_skull_mask,
                                                                          pfi_affine_transformation_1305_bicom_on_b0,
                                                                          pfi_roi_mask)

        print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
        print_and_run(cmd_1, safety_on=control['safety_on'])
        print_and_run(cmd_2, safety_on=control['safety_on'])

    if control['step_dilate_mask']:

        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask, dil_factor, pfi_roi_mask_dilated)
        print_and_run(cmd, msg='Dilate mask ' + sj, safety_on=control['safety_on'])

    if control['step_cut_to_mask_dwi']:

        print '\nCutting newly-created ROI mask on the subject: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            cut_dwi_image_from_first_slice_mask_path(pfi_dwi_squeezed,
                                                     pfi_roi_mask_dilated,
                                                     pfi_dwi_cropped_to_roi)

    if control['step_correct_the_slope']:

        print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            slope_corrector_path(pfi_slopes_txt_file, pfi_dwi_cropped_to_roi, pfi_dwi_slope_corrected)

    """ *** PHASE 2 - EDDY CURRENTS CORRECTION and analysis *** """

    if control['step_eddy_current_corrections']:

        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd, msg='\n Eddy currents correction: subject {}.\n'.format(sj), safety_on=control['safety_on'])

    if control['step_dwi_analysis_with_fsl']:

        here = os.getcwd()

        cmd0 = 'cd {}'.format(outputs_folder)
        cmd1 = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
              '-w --save_tensor -o {4}'.format(pfi_dwi_slope_corrected,
                                               pfi_input_bvals,
                                               pfi_input_bvects,
                                               pfi_roi_mask_dilated,
                                               pfi_analysis_fsl)
        cmd2 = 'cd {}'.format(here)

        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, msg='DWI analysis: subject ' + sj, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])

    """ *** PHASE 2bis - POST-PROCESSING *** """

    if control['step_orient_directions']:

        for fn in fn_results_to_keep:

            pfi_im = jph(outputs_folder, fn)
            name_reoriented = 'reoriented_' + fn.split('.')[0] + '.nii.gz'
            pfi_im_new = jph(outputs_folder, name_reoriented)

            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_im, pfi_im_new)

            print_and_run(cmd, msg='Reorient ' + sj + ' ' + fn, safety_on=control['safety_on'])

        cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_roi_mask_dilated, pfi_mask_reoriented)

        print_and_run(cmd, msg='Reorient mask ' + sj, safety_on=control['safety_on'])

    """ *** PHASE 3 - ORIENT RESULTS IN HISTOLOGICAL COORDINATES *** """  # Usare T1 invece!!!!

    if control['step_orient_histo']:

        # take the absolute values of V1
        pfi_V1 = jph(outputs_folder, 'reoriented_fsl_dtifit_' + sj + '_V1.nii.gz')
        cmd = 'seg_maths {0} -abs {0}'.format(pfi_V1)
        print_and_run(cmd, safety_on=control['safety_on'])

        for fn in fn_results_to_keep:

            name_input = 'reoriented_' + fn
            pfi_input = jph(outputs_folder, name_input)
            pfi_output = jph(outputs_folder, prefix_histo + fn.split('.')[0] + '.nii.gz')

            if fn.split('.')[0].endswith('V1'):

                reproduce_slice_fourth_dimension_path(pfi_mask_reoriented, pfi_mask_reoriented_V1, num_slices=3)





                cmd = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(
                        T1_in_histological_coordinates,
                        pfi_input,
                        T1_in_histological_coordinates_brain_mask,
                        pfi_mask_reoriented_V1,
                        pfi_affine_transformation_to_histological,
                        pfi_output)

                print '\n Alignment in histological coordinates, subject {0}, {1}.\n'.format(sj, fn)
                print_and_run(cmd, safety_on=control['safety_on'])

            elif fn.split('.')[0].endswith('or'):

                reproduce_slice_fourth_dimension_path(pfi_mask_reoriented, pfi_mask_reoriented_tensor, num_slices=6)

                cmd = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(
                        T1_in_histological_coordinates,
                        pfi_input,
                        T1_in_histological_coordinates_brain_mask,
                        pfi_mask_reoriented_V1,
                        pfi_affine_transformation_to_histological,
                        pfi_output)

                print '\n Alignment in histological coordinates, subject {0}, {1}.\n'.format(sj, fn)
                print_and_run(cmd, safety_on=control['safety_on'])

            else:

                cmd = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(
                        T1_in_histological_coordinates,
                        pfi_input,
                        T1_in_histological_coordinates_brain_mask,
                        pfi_mask_reoriented,
                        pfi_affine_transformation_to_histological,
                        pfi_output)

                print '\n Alignment in histological coordinates, subject {0}, {1}.\n'.format(sj, fn)
                print_and_run(cmd, safety_on=control['safety_on'])

                print '\n Adjust the warped with a threshold to avoid negative: ' \
                      'subj {0}, file {1}.\n'.format(sj, fn)

                cmd = 'seg_maths {0} -thr 0 {0}'.format(pfi_output)
                print_and_run(cmd, safety_on=control['safety_on'])

    if control['step_bfc_b0']:

        pfi_S0 = jph(outputs_folder, prefix_histo + prefix_fsl_output + sj + '_S0.nii.gz')

        print '\nBias field correction: subject {}.\n'.format(sj)

        if not control['safety_on']:
            bias_field_correction(pfi_S0, pfi_S0,
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

    """ *** PHASE 4 - MOVE RESULTS IN THE APPROPRIATE FOLDER OF THE FOLDER STRUCTURE *** """

    if control['step_save_results_histo']:

        for fn in fn_results_to_keep:

            name_original = 'histo_' + fn.split('.')[0] + '.nii.gz'
            pfi_original = jph(outputs_folder, name_original)

            name_moved = sj + '_' + fn.split('.')[0][-2:] + '.nii.gz'
            pfi_moved = jph(root, sj, 'all_modalities', name_moved)

            cmd = 'cp {0} {1} '.format(pfi_original, pfi_moved)

            print_and_run(cmd, msg='Moving from original in the output folder to the new folder',
                          safety_on=control['safety_on'])

    """ *** PHASE 5 - ERASE THE INTERMEDIATE RESULTS *** """

    if control['delete_intermediate_steps']:

        cmd = 'rm -r {0} '.format(outputs_folder)
        print_and_run(cmd, msg='Erasing pre_process_DWI folder for subject {}.'.format(sj),
                      safety_on=control['safety_on'])
