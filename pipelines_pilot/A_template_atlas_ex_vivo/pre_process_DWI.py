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
from tools.parsers.separate_shells import separate_shells_txt_path, separate_shells_dwi_path


def process_DWI(sj, delete_intermediate_steps=True):

    #################
    # paths manager #
    #################

    root = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

    # path to DWI data subject

    path_dwi_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.nii.gz')
    path_dwi_txt_data_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.txt')

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

    outputs_folder = jph(root, sj, 'all_modalities', 'pre_process_DWI')

    # ----- # in case the timepoints are in the 5th rather than the fourth dim
    step_squeeze                    = False

    path_dwi_squeezed = jph(outputs_folder, sj + '_DWI_squeezed.nii.gz')

    # ----- # Output filenames are the default: 'DwDir.txt', 'DwEffBval.txt', 'DwGradVec.txt', 'VisuCoreDataSlope.txt'
    step_extract_bval_bvect_slope   = False

    # ----- #
    step_extract_first_timepoint       = False

    path_dwi_b0 = jph(outputs_folder, sj + '_DWI_first_timepoint.nii.gz')

    # ----- #
    step_grab_the_roi_mask         = False

    path_affine_transformation_1305_bicom_on_b0 = jph(outputs_folder, sj + '_affine_transf_1305_bicom_on_b0.txt')
    path_warped_1305_bicom_on_b0 = jph(outputs_folder, sj + '_warped_1305_bicom_on_b0.nii.gz')
    suffix_command_reg_1305_bicom_on_b0 = ''
    path_roi_mask = jph(outputs_folder, sj + '_roi_mask.nii.gz')

    # ----- #
    step_dilate_mask             = True

    dil_factor = 0
    path_roi_mask_dilated = jph(outputs_folder, sj + '_roi_mask_dilated.nii.gz')

    # ----- #
    step_cut_to_mask_dwi        = True

    path_dwi_cropped_to_roi = jph(outputs_folder, sj + 'DWI_roi_cropped.nii.gz')

    # ----- #
    step_correct_the_slope    = True

    path_slopes_txt_file = jph(outputs_folder, sj + '_VisuCoreDataSlope.txt')
    path_dwi_slope_corrected = jph(outputs_folder, sj + '_DWI_slope_corrected.nii.gz')

    # ----- # FIT analysis
    step_dwi_analysis_with_nifty_fit   = False

    path_folder_analysis_fit = jph(outputs_folder, 'analysis_fit')

    path_dwi_bvals   = jph(outputs_folder, sj + '_DwEffBval.txt')
    path_dwi_bvects  = jph(outputs_folder, sj + '_DwGradVec.txt')

    path_fit_dti     = jph(path_folder_analysis_fit, sj + '_v1map.nii.gz')
    path_fit_rgb_map = jph(path_folder_analysis_fit, sj + '_rgbmap.nii.gz')
    path_fit_adc_map = jph(path_folder_analysis_fit, sj + '_adcmap.nii.gz')
    path_fit_fa_map  = jph(path_folder_analysis_fit, sj + '_famap.nii.gz')
    # path_fit_noddi = jph(path_output_folder, sj + '_noddi.nii.gz')

    # ----- # FIT reorientation
    step_reorient_output_of_nifty_fit   = False

    path_fit_dti_oriented     = jph(path_folder_analysis_fit, sj + '_histo_oriented_v1map.nii.gz')
    path_fit_rgb_map_oriented = jph(path_folder_analysis_fit, sj + '_histo_oriented_rgbmap.nii.gz')
    path_fit_adc_map_oriented = jph(path_folder_analysis_fit, sj + '_histo_oriented_adcmap.nii.gz')
    path_fit_fa_map_oriented  = jph(path_folder_analysis_fit, sj + '_histo_oriented_famap.nii.gz')

    # ----- # FSL analysis
    step_dwi_analysis_with_nifty_fsl     = True

    path_folder_analysis_fsl = jph(outputs_folder, 'analysis_fsl')

    # ----- # FSL reorientation
    step_reorient_output_of_fsl = True

    # ----- # FSL analysis divided by shells
    # divide txt files with bvals, bvects
    step_divide_bval_bvect_by_shells  = False

    num_shells = 3

    # ----- # divide dwi images by shells:
    step_divide_dwi_by_shells   = False

    # ----- # analyse images by shells:
    step_dwi_analysis_divided_by_shells_with_fsl = False

    path_folder_analysis_fsl_divided_by_shells = jph(outputs_folder, 'analysis_fsl_divided_by_shells')

    # ----- # reorient outcome of the analysis divided by shells:
    step_dwi_reorient_fit_divided_by_shells = False

    # --------- # Copy results in the appropriate place in the folder structure
    step_save_results = False

    path_to_T1_final = jph(root, sj, 'all_modalities', sj + '_T1.nii.gz')

    path_to_masks_final = jph(root, sj, 'masks')
    path_to_roi_mask_final = jph(path_to_masks_final, sj + '_roi_mask.nii.gz')

    # --------- # Save processing in bicommissural orientation, with no resampling errors,
    # will be used for DWI processing.  TODO, not needed for the moment.
    step_save_bicommissural = False

    # --------- # erase the intermediate results folder
    step_erase_intemediate_results_folder = delete_intermediate_steps

    ##################
    # PIPELINE:      #
    ##################

    """ *** PHASE 1 - DWI PROCESSING IN BICOMMISSURAL COORDINATES *** """

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
            squeeze_image_from_path(path_dwi_original, path_dwi_squeezed, copy_anyway=True)

    if step_extract_bval_bvect_slope:

        if verbose_on:
            print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            parse_bruker_dwi_txt(path_dwi_txt_data_original,
                                 output_folder=outputs_folder,
                                 prefix=sj + '_')

    if step_extract_first_timepoint:

        if verbose_on:
            print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not safety_on:

            nib_dwi = nib.load(path_dwi_squeezed)
            # Extract first slice and save as the fixed image - Keep the same header.
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, path_dwi_b0)

    if step_grab_the_roi_mask:

        # reference is the b0: path_dwi_b0
        # floating is the reference T1 in bicommissural: s_1305_with_roi
        # mask to be propagated is: s_1305_with_roi_brain_skull_mask

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(path_dwi_b0,
                                                                               s_1305_with_roi,
                                                                               path_affine_transformation_1305_bicom_on_b0,
                                                                               path_warped_1305_bicom_on_b0,
                                                                               suffix_command_reg_1305_bicom_on_b0)
        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_dwi_b0,
                                                                                      s_1305_with_roi_brain_skull_mask,
                                                                                      path_affine_transformation_1305_bicom_on_b0,
                                                                                      path_roi_mask)

        if verbose_on:
            print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
            print cmd_1
            print cmd_2

        if not safety_on:
            os.system(cmd_1 + cmd_2)

    if step_dilate_mask:

        cmd = 'seg_maths {0} -dil {1} {2}'.format(path_roi_mask, dil_factor, path_roi_mask_dilated)

        if verbose_on:
            print cmd

        if not safety_on:
            os.system(cmd)

    if step_cut_to_mask_dwi:

        if verbose_on:
            print '\nCutting newly-created ROI mask on the subject: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            cut_dwi_image_from_first_slice_mask_path(path_dwi_squeezed,
                                                     path_roi_mask_dilated,
                                                     path_dwi_cropped_to_roi)

    if step_correct_the_slope:

        # correct the slope on the trimmed image

        if verbose_on:
            print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            slope_corrector_path(path_slopes_txt_file, path_dwi_cropped_to_roi, path_dwi_slope_corrected)

    """ *** PHASE 2 - FIT ANALYSIS *** """

    if step_dwi_analysis_with_nifty_fit:

        # create the folder analysis_fit if nor present:
        cmd_0 = 'mkdir -p {0}'.format(path_folder_analysis_fit)

        cmd = 'fit_dwi -source {0} -bval {1} -bvec {2} -mask {3} ' \
              '-v1map {4} -rgbmap {5} -mdmap {6} -famap {7}'.format(path_dwi_slope_corrected,
                                                         path_dwi_bvals,
                                                         path_dwi_bvects,
                                                         path_roi_mask_dilated,
                                                         path_fit_dti,
                                                         path_fit_rgb_map,
                                                         path_fit_adc_map,
                                                         path_fit_fa_map)

        print 'NIFTY FIT analysis!'
        print cmd

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd)

    if step_reorient_output_of_nifty_fit:

        list_paths = [path_fit_dti, path_fit_rgb_map, path_fit_adc_map, path_fit_fa_map]
        list_paths_new = [path_fit_dti_oriented, path_fit_rgb_map_oriented, path_fit_adc_map_oriented,
                          path_fit_fa_map_oriented]

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for im, im_new in zip(list_paths, list_paths_new):
            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(im, im_new)
            print cmd
            if not safety_on:
                os.system(cmd)

    """ *** PHASE 3 - FSL ANALYSIS *** """

    if step_dwi_analysis_with_nifty_fsl:

        # dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT

        cmd_0 = 'mkdir -p {0}'.format(path_folder_analysis_fsl)

        cmd = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
              '-w --save_tensor -o {4}'.format(path_dwi_slope_corrected,
                                               path_dwi_bvals,
                                               path_dwi_bvects,
                                               path_roi_mask_dilated,
                                               path_folder_analysis_fsl)

        print cmd

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd)

    if step_reorient_output_of_fsl:

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for (dirpath, dirnames, filenames) in os.walk(path_folder_analysis_fsl):
            for filename in filenames:
                if filename.endswith('.nii.gz') or filename.endswith('.nii'):
                    im = os.path.join(dirpath, filename)
                    im_name_reoriented = 'reoriented_' + filename.split('.')[0] + '.nii.gz'
                    im_new = os.path.join(dirpath, im_name_reoriented)

                    cmd = ''' cp {0} {1};
                              fslorient -deleteorient {1};
                              fslswapdim {1} -z -y -x {1};
                              fslorient -setqformcode 1 {1};'''.format(im, im_new)
                    print cmd

                    if not safety_on:
                        os.system(cmd)

    """ *** PHASE 4 - FSL ANALYSIS DIVIDED BY SHELLS *** """

    if step_divide_bval_bvect_by_shells:

        cmd_0 = 'mkdir -p {0}'.format(path_folder_analysis_fsl_divided_by_shells)

        print 'Separate b-vals and b-vect by shells: execution for subject {0}'.format(sj)

        if not safety_on:
            os.system(cmd_0)
            separate_shells_txt_path(path_dwi_bvals,
                                     path_dwi_bvects,
                                     output_folder=path_folder_analysis_fsl_divided_by_shells,
                                     prefix=sj,
                                     num_initial_dir_to_skip=1,
                                     num_shells=num_shells)

    if step_divide_dwi_by_shells:

        print 'Separate dwi by shells: execution for subject {0}'.format(sj)

        if not safety_on:
            separate_shells_dwi_path(path_dwi_slope_corrected,
                                     output_folder=path_folder_analysis_fsl_divided_by_shells,
                                     prefix=sj,
                                     suffix='_DWI_shell_',
                                     num_initial_dir_to_skip=1,
                                     num_shells=num_shells)

    if step_dwi_analysis_divided_by_shells_with_fsl:
        # dtifit -k ScaledData.nii.gz -b DwEffBval.txt -r bvecs.txt -m Brain_mask.nii.gz  -w --save_tensor -o DTI/DT

        for sh in range(num_shells):

            # Analysis for each shell:
            path_folder_shell_sh_data = jph(path_folder_analysis_fsl_divided_by_shells, 'shell_' + str(sh))

            # create the folder analysis_fit if nor present:
            cmd_0 = 'mkdir -p {0}'.format(path_folder_shell_sh_data)

            path_input_dwi_shell_sh   = jph(path_folder_analysis_fsl_divided_by_shells,
                                            sj + '_DWI_shell_' + str(sh) + 'nii.gz')
            path_input_bval_shell_sh  = jph(path_folder_analysis_fsl_divided_by_shells,
                                            sj + '_DwEffBval_shell' + str(sh) + '.txt')
            path_input_bvect_shell_sh = jph(path_folder_analysis_fsl_divided_by_shells,
                                            sj + '_DwGradVec_shell' + str(sh) + '.txt')

            cmd = 'dtifit -k {0} -b {1} -r {2} -o {4}'.format(path_input_dwi_shell_sh,
                                                              path_input_bval_shell_sh,
                                                              path_input_bvect_shell_sh,
                                                              path_folder_shell_sh_data)

            print '\nPerform DWI analysis by shells: execution for subject {0} and for shell {1}\n'.format(sj, sh)

            print cmd

            if not safety_on:
                os.system(cmd_0)
                os.system(cmd)

    if step_dwi_reorient_fit_divided_by_shells:

        print '\nReorient: execution, fsl divided by shells, for subject {0}.\n'.format(sj)

        for (dirpath, dirnames, filenames) in os.walk(path_folder_analysis_fsl_divided_by_shells):
            for filename in filenames:
                if filename.endswith('.nii.gz') or filename.endswith('.nii'):
                    im = os.path.join(dirpath, filename)
                    im_name_reoriented = 'reoriented_' + filename.split('.')[0] + '.nii.gz'
                    im_new = os.path.join(dirpath, im_name_reoriented)

                    cmd = ''' cp {0} {1};
                              fslorient -deleteorient {1};
                              fslswapdim {1} -z -y -x {1};
                              fslorient -setqformcode 1 {1};'''.format(im, im_new)
                    print cmd

                    if not safety_on:
                        os.system(cmd)

    """ *** PHASE 5 - ORIENT RESULTS IN HISTOLOGICAL COORDINATES *** """

    """ *** PHASE 6 - DUPLICATE RESULTS IN THE FOLDER STRUCTURE *** """

    """ *** PHASE 7 - DUPLICATE RESULTS BICOMMISSURAL ORIENTATION AS WELL *** """
    # not needed for the moment.

    """ *** PHASE 8 - ERASE THE INTERMEDIATE RESULTS *** """





