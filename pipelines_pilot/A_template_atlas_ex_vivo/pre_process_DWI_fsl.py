"""
Process and align DWI in histological orientation.
"""
import os
from os.path import join as jph
import nibabel as nib

from definitions import root_pilot_study
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data
from tools.parsers.parse_bruker_txt import parse_bruker_dwi_txt
from tools.correctors.slope_corrector import slope_corrector_path


def process_DWI_fsl(sj, delete_intermediate_steps=True):

    #################
    # paths manager #
    #################

    root = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

    # path to DWI data subject

    pfi_dwi_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.nii.gz')
    pfi_dwi_txt_data_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.txt')

    # subject 1305 with region of interest (brain + skull) masks:

    s_1305_with_roi = jph(root, 'Utils', '1305_brain_and_skull_mask_T1_dwi_oriented', '1305_T1.nii.gz')
    s_1305_with_roi_brain_skull_mask = jph(root, 'Utils', '1305_brain_and_skull_mask_T1_dwi_oriented', '1305_T1_roi_mask.nii.gz')

    # subject 1305 manually oriented in histological coordinates

    s_1305_in_histological_coordinates = jph(root, 'Utils', '1305_histological_orientation', '1305_T1.nii.gz')
    s_1305_in_histological_coordinates_brain_mask = jph(root, 'Utils', '1305_histological_orientation', '1305_T1_roi_mask.nii.gz')

    ####################
    # Controller:      #
    ####################

    safety_on = False
    verbose_on = True

    # --------- #
    step_generate_output_folder = False

    outputs_folder = jph(root, sj, 'all_modalities', 'pre_process_DWI_fsl')

    # ----- # in case the timepoints are in the 5th rather than the fourth dim
    step_squeeze                    = False

    pfi_dwi_squeezed = jph(outputs_folder, sj + '_DWI_squeezed.nii.gz')

    # ----- # Output filenames (fn) are the default: 'DwDir.txt', 'DwEffBval.txt', 'DwGradVec.txt', 'VisuCoreDataSlope.txt'
    step_extract_bval_bvect_slope   = False

    pfi_input_bvals   = os.path.join(outputs_folder, sj + '_DwEffBval.txt')
    pfi_input_bvects  = os.path.join(outputs_folder, sj + '_DwGradVec.txt')
    pfi_slopes_txt_file = jph(outputs_folder, sj + '_VisuCoreDataSlope.txt')

    # ----- #
    step_extract_first_timepoint       = False

    pfi_dwi_b0 = jph(outputs_folder, sj + '_DWI_first_timepoint.nii.gz')

    # ----- #
    step_grab_the_roi_mask         = False

    pfi_affine_transformation_1305_bicom_on_b0 = jph(outputs_folder, sj + '_affine_transf_1305_bicom_on_b0.txt')
    pfi_warped_1305_bicom_on_b0 = jph(outputs_folder, sj + '_warped_1305_bicom_on_b0.nii.gz')
    suffix_command_reg_1305_bicom_on_b0 = ''
    pfi_roi_mask = jph(outputs_folder, sj + '_roi_mask.nii.gz')

    # ----- #
    step_dilate_mask             = False

    dil_factor = 0
    pfi_roi_mask_dilated = jph(outputs_folder, sj + '_roi_mask_dilated.nii.gz')

    # ----- #
    step_cut_to_mask_dwi        = False

    pfi_dwi_cropped_to_roi = jph(outputs_folder, sj + '_DWI_roi_cropped.nii.gz')

    # ----- #
    step_correct_the_slope    = False

    pfi_dwi_slope_corrected = jph(outputs_folder, sj + '_DWI_slope_corrected.nii.gz')

    # ----- # FSL Eddy currents correction:
    step_eddy_current_corrections     = True

    prefix_dwi_eddy_corrected = 'fsl_eddy_corrected_'
    pfi_dwi_eddy_corrected    = jph(outputs_folder, prefix_dwi_eddy_corrected + '.nii.gz')

    # ----- # FSL analysis
    step_dwi_analysis_with_fsl     = False

    name_for_analysis_fsl = 'fsl_dtifit_'

    suffix_results_to_keep = ['FA', 'MD', 'V1', 'tensor', 'S0']
    fn_results_to_keep = [name_for_analysis_fsl + sj + pref + '.nii.gz' for pref in suffix_results_to_keep]

    # ----- # FSL reorientation
    step_provide_correct_orientation_labels = False

    pfi_mask_reoriented = jph(outputs_folder, sj + '_roi_mask_dilated_oriented.nii.gz')


    # ----- # reorient outcome of the analysis divided by shells:
    step_orient_histological = False

    pfi_affine_transformation_to_histological = jph(outputs_folder, sj + '_transf_to_histological.txt')
    pfi_DWI_histological = jph(outputs_folder, sj + '_DWI_in_histological.nii.gz')
    pfi_mask_histological = jph(outputs_folder, sj + '_DWI_mask_in_histological.nii.gz')

    # --------- # Copy results in the appropriate place in the folder structure
    step_save_results_histological = False

    pfo_masks_final = jph(root, sj, 'masks')
    pfi_roi_mask_final = jph(pfo_masks_final, sj + '_roi_mask.nii.gz')


    # --------- # erase the intermediate results folder
    step_erase_intemediate_results_folder = delete_intermediate_steps

    ##################
    # PIPELINE:      #
    ##################

    """ *** PHASE 1 - DWI PRE-PROCESSING IN BICOMMISSURAL COORDINATES *** """

    if step_generate_output_folder:

        cmd = 'mkdir -p ' + outputs_folder
        if verbose_on:
            print cmd
        if not safety_on:
            os.system(cmd)

    if step_squeeze:

        if verbose_on:
            print '\n Squeeze for DWI images: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            squeeze_image_from_path(pfi_dwi_original, pfi_dwi_squeezed, copy_anyway=True)

    if step_extract_bval_bvect_slope:

        if verbose_on:
            print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            parse_bruker_dwi_txt(pfi_dwi_txt_data_original,
                                 output_folder=outputs_folder,
                                 prefix=sj + '_')

    if step_extract_first_timepoint:

        if verbose_on:
            print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not safety_on:

            nib_dwi = nib.load(pfi_dwi_squeezed)
            # Extract first slice and save as the fixed image - Keep the same header.
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, pfi_dwi_b0)

    if step_grab_the_roi_mask:

        # reference is the b0: path_dwi_b0
        # floating is the reference T1 in bicommissural: s_1305_with_roi
        # mask to be propagated is: s_1305_with_roi_brain_skull_mask

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(pfi_dwi_b0,
                                                                       s_1305_with_roi,
                                                                       pfi_affine_transformation_1305_bicom_on_b0,
                                                                       pfi_warped_1305_bicom_on_b0,
                                                                       suffix_command_reg_1305_bicom_on_b0)
        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(pfi_dwi_b0,
                                                                          s_1305_with_roi_brain_skull_mask,
                                                                          pfi_affine_transformation_1305_bicom_on_b0,
                                                                          pfi_roi_mask)

        if verbose_on:
            print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
            print cmd_1
            print cmd_2

        if not safety_on:
            os.system(cmd_1 + cmd_2)

    if step_dilate_mask:

        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask, dil_factor, pfi_roi_mask_dilated)

        if verbose_on:
            print cmd

        if not safety_on:
            os.system(cmd)

    if step_cut_to_mask_dwi:

        if verbose_on:
            print '\nCutting newly-created ROI mask on the subject: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            cut_dwi_image_from_first_slice_mask_path(pfi_dwi_squeezed,
                                                     pfi_roi_mask_dilated,
                                                     pfi_dwi_cropped_to_roi)

    if step_correct_the_slope:

        if verbose_on:
            print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            slope_corrector_path(pfi_slopes_txt_file, pfi_dwi_cropped_to_roi, pfi_dwi_slope_corrected)

    """ *** PHASE 2 - EDDY CURRENTS CORRECTION and analysis *** """
    # https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/UsersGuide

    if step_eddy_current_corrections:

        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)

        if verbose_on:
            print '\n Eddy currents correction: subject {}.\n'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)

    if step_dwi_analysis_with_fsl:

        if os.path.isfile(pfi_dwi_eddy_corrected):
            pfi_last_dwi = pfi_dwi_eddy_corrected
        else:
            pfi_last_dwi = pfi_dwi_slope_corrected

        cmd = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
              '-w --save_tensor -o {4}'.format(pfi_last_dwi,
                                               pfi_input_bvals,
                                               pfi_input_bvects,
                                               pfi_roi_mask_dilated,
                                               name_for_analysis_fsl)

    """ *** PHASE 2bis - POST-PROCESSING *** """

    if step_provide_correct_orientation_labels:

        # copy the output for some new image! It is not idempotent!

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for fn in fn_results_to_keep:

            pfi_im = jph(outputs_folder, fn)
            name_reoriented = 'reoriented_' + fn.split('.')[0] + '.nii.gz'
            pfi_im_new = jph(outputs_folder, name_reoriented)

            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_im, pfi_im_new)
            print cmd

            if not safety_on:
                os.system(cmd)

        print '\nReorient mask: subject {}.\n'.format(sj)

        cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_roi_mask_dilated, pfi_mask_reoriented)

        if not safety_on:
                os.system(cmd)

    """ *** PHASE 3 - ORIENT RESULTS IN HISTOLOGICAL COORDINATES *** """
    if step_orient_histological:

        for fn in fn_results_to_keep:

            name_input = 'reoriented_' + fn.split('.')[0] + '.nii.gz'
            pfi_input = jph(outputs_folder, name_input)

            cmd0 = 'reg_aladin -ref {0} -flo {1} -rmask {2} -fmask {3} -aff {4} -res {5} -rigOnly ; '.format(s_1305_in_histological_coordinates,
                                                                         pfi_input,
                                                                         s_1305_in_histological_coordinates_brain_mask,
                                                                         pfi_mask_reoriented,
                                                                         pfi_affine_transformation_to_histological,
                                                                         pfi_DWI_histological)

            cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(s_1305_in_histological_coordinates,
                                                                            pfi_mask_reoriented,
                                                                            pfi_affine_transformation_to_histological,
                                                                            pfi_mask_histological)

            if verbose_on:
                print '\n Alignment in histological coordinates, subject {}.\n'.format(sj)

            if not safety_on:
                os.system(cmd0 + cmd1)

            if name_input.split('.')[0].endswith('FA') \
                    or name_input.split('.')[0].endswith('MD') \
                    or name_input.split('.')[0].endswith('S0'):

                if verbose_on:
                    print '\n Adjust the warped with a threshold to avoid negative: ' \
                          'subj {0}, file {1}.\n'.format(sj, fn)

                    cmd = 'seg_maths {0} -thr 0 {0}'.format(pfi_input)

                    if not safety_on:
                        os.system(cmd)

    """ *** PHASE 4 - MOVE RESULTS IN THE APPROPRIATE FOLDER OF THE FOLDER STRUCTURE *** """

    if step_save_results_histological:

        for fn in fn_results_to_keep:

            name_original = 'reoriented_' + fn.split('.')[0] + '.nii.gz'
            pfi_original = jph(outputs_folder, name_original)

            name_moved = sj + '_' + fn.split('.')[0][-2] + '.nii.gz'
            pfi_moved = jph(root, sj, 'all_modalities', name_moved)

            cmd = 'mv {0} {1} '.format(pfi_original, pfi_moved)

            if verbose_on:
                print 'Moving from original in the output folder to the new folder '

            if not safety_on:
                os.system(cmd)

    """ *** PHASE 5 - ERASE THE INTERMEDIATE RESULTS *** """

    if step_erase_intemediate_results_folder:

        cmd = 'rm -r {0} '.format(outputs_folder)

        if verbose_on:
            print 'Eraseing pre_process_DWI folder for subject {}.'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)





