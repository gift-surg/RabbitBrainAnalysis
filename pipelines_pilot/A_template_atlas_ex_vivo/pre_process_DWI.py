"""
Align T1 in histological orientation after standard pre-processing.
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

    # path to T1 of the same subject with region of interest (bicommissural orientation):

    path_to_bicommissural_folder = jph(root, sj, 'bicommissural')
    path_to_T1_bicommissural_final = jph(path_to_bicommissural_folder, sj + '_T1_bicommissural.nii.gz')
    path_to_T1_bicommissural_final_roi_mask = jph(path_to_bicommissural_folder, sj + '_T1_bicommissural_brain_skull_mask.nii.gz')

    ####################
    # Controller:      #
    ####################

    safety_on = False
    verbose_on = True

    # --------- #
    step_generate_output_folder = True

    outputs_folder = jph(root, sj, 'all_modalities', 'pre_process_DWI')

    # ----- # in case the timepoints are in the 5th rather than the fourth dim
    step_squeeze                    = True

    path_dwi_squeezed = jph(outputs_folder, sj + '_DWI_squeezed.nii.gz')

    # ----- # Output filenames are the default: # TODO
    step_extract_bval_bvect_slope   = True

    # ----- #
    step_extract_first_timepoint       = False

    path_dwi_b0 =

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
            squeeze_image_from_path(path_dwi_original, path_dwi_squeezed)

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

            nib_dwi = nib.load(path_dwi)
            # Extract first slice and save as the fixed image - Keep the same header.
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib.load(path_dwi), nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, path_first_slice_dwi_extracted)

    """ Create the 1-time dimension DWI mask """
    if step_create_1d_layer_mask:

        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_ex_vivo_dwi, sj, 'transformations'))

        path_oriented_as_dwi_1305_3d_template = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D.nii.gz')
        path_oriented_as_dwi_1305_3d_ciccione = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D_mask_fin_dil5.nii.gz')

        path_affine_transformation_output = os.path.join(root_ex_vivo_dwi, sj, 'transformations',
                                                         sj + '_on_unoriented_1305.txt')
        path_3d_warped_output = os.path.join(root_ex_vivo_dwi, 'zz_trash', sj + '_on_unoriented_1305.nii.gz')

        path_mask_output = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly ; '.format(path_first_slice_dwi_extracted,
                                                                             path_oriented_as_dwi_1305_3d_template,
                                                                             path_affine_transformation_output,
                                                                             path_3d_warped_output)

        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_first_slice_dwi_extracted,
                                                                                 path_oriented_as_dwi_1305_3d_ciccione,
                                                                                 path_affine_transformation_output,
                                                                                 path_mask_output)

        if verbose_on:
            print '\n Register and propagate ciccione to first slice and save the registered ciccione:' \
                  ' execution for subject {0}.\n'.format(sj)
            print cmd_1
            print cmd_2

        if not safety_on:
            os.system(cmd_0)
            # Register and propagate ciccione to first slice and save the registered ciccione -
            # same header of the 3d image.
            os.system(cmd_1 + cmd_2)

    """ dilate the newly created mask for safety reasons. """
    if step_dilate_mask:

        path_mask = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')
        cmd = 'seg_maths {0} -dil {1} {0}'.format(path_mask, dil_mask_factor)

        if verbose_on:
            print cmd

        if not safety_on:
            os.system(cmd)

    """ cut the mask from the anatomical images - this will reduce the size of the DWI significantly """
    if step_cut_to_mask_dwi:

        path_dwi_nii_input = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        path_3d_nii_mask_for_dwi = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')
        path_dwi_cropped_roi_result = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped.nii.gz')

        if verbose_on:
            print '\nCutting newly-created ciccione mask on the subject: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            cut_dwi_image_from_first_slice_mask_path(path_dwi_nii_input,
                                                     path_3d_nii_mask_for_dwi,
                                                     path_dwi_cropped_roi_result)

    """ Correct for the slopes on the trimmed images """
    if step_correct_the_slope:

        path_slopes_txt_input = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_VisuCoreDataSlope.txt')

        path_3d_cropped_roi = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped.nii.gz')
        path_3d_sloped_cropped_result = os.path.join(root_ex_vivo_dwi, sj, 'DWI',
                                                     sj + '_DWI_cropped_and_slope_corrected.nii.gz')

        if verbose_on:
            print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            slope_corrector_path(path_slopes_txt_input, path_3d_cropped_roi, path_3d_sloped_cropped_result)

    ###############################
    # DO THE ANALYSIS # NIFTY FIT #
    ###############################

    """ Perform the DWI analysi - nifty_fit """
    if step_dwi_analysis_nifty_fit:

        path_input_dwi    = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped_and_slope_corrected.nii.gz')
        path_input_bval   = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwEffBval.txt')
        path_input_bvect  = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwGradVec.txt')
        path_input_mask   = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')

        path_output_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit')
        path_output_dti    = os.path.join(path_output_folder, sj + '_v1map.nii.gz')
        path_output_rgb_map = os.path.join(path_output_folder, sj + '_rgbmap.nii.gz')
        path_output_adc_map = os.path.join(path_output_folder, sj + '_adcmap.nii.gz')
        path_output_fa_map = os.path.join(path_output_folder, sj + '_famap.nii.gz')
        # path_output_noddi = os.path.join(path_output_folder, sj + '_noddi.nii.gz')

        # create the folder analysis_fit if nor present:
        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit'))

        cmd = 'fit_dwi -source {0} -bval {1} -bvec {2} -mask {3} ' \
              '-v1map {4} -rgbmap {5} -mdmap {6} -famap {7}'.format(path_input_dwi,
                                                         path_input_bval,
                                                         path_input_bvect,
                                                         path_input_mask,
                                                         path_output_dti,
                                                         path_output_rgb_map,
                                                         path_output_adc_map,
                                                         path_output_fa_map)

        print cmd

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd)

    """ REORIENT output - only after all the analysis!!! """
    if step_reorient_nifty_fit:

        # copy the output for some new image! It is not idempotent!

        path_images_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit')

        path_dti    = os.path.join(path_images_folder, sj + '_v1map.nii.gz')
        path_rgb_map = os.path.join(path_images_folder, sj + '_rgbmap.nii.gz')
        path_adc_map = os.path.join(path_images_folder, sj + '_adcmap.nii.gz')
        path_fa_map = os.path.join(path_images_folder, sj + '_famap.nii.gz')
        # path_noddi = os.path.join(path_images_folder, sj + '_noddi.nii.gz')

        path_dti_new    = os.path.join(path_images_folder, sj + '_reoriented_v1map.nii.gz')
        path_rgb_map_new = os.path.join(path_images_folder, sj + '_reoriented_rgbmap.nii.gz')
        path_adc_map_new = os.path.join(path_images_folder, sj + '_reoriented_adcmap.nii.gz')
        path_fa_map_new = os.path.join(path_images_folder, sj + '_reoriented_famap.nii.gz')
        # path_noddi_new = os.path.join(path_images_folder, sj + '_reoriented_noddi.nii.gz')

        list_paths = [path_dti, path_rgb_map, path_adc_map, path_fa_map]

        list_paths_new = [path_dti_new, path_rgb_map_new, path_adc_map_new, path_fa_map_new]

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for im, im_new in zip(list_paths, list_paths_new):
            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(im, im_new)
            print cmd
            if not safety_on:
                os.system(cmd)

    #########################
    # DO THE ANALYSIS # FSL #
    #########################

    """ Perform the DWI analysi - FSL """
    # dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT
    if step_dwi_analysis_fsl:

        path_input_dwi    = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped_and_slope_corrected.nii.gz')
        path_input_bval   = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwEffBval.txt')
        path_input_bvect  = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwGradVec.txt')
        path_input_mask   = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')

        path_output_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fsl')
        path_output_dti    = os.path.join(root_ex_vivo_dwi, sj + '_dti_')

        # create the folder analysis_fit if nor present:
        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_ex_vivo_dwi, sj, 'analysis_fsl'))

        cmd = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
              '-w --save_tensor -o {4}'.format(path_input_dwi,
                                               path_input_bval,
                                               path_input_bvect,
                                               path_input_mask,
                                               path_output_dti)

        print cmd

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd)

    """ REORIENT output - only after all the analysis IN THIS VERSION. """
    if step_reorient_fsl:

        # copy the output for some new image! It is not idempotent!

        path_images_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fsl')

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for (dirpath, dirnames, filenames) in os.walk(path_images_folder):
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

    #####################################
    # DO THE ANALYSIS DIVIDED BY SHELLS #
    #####################################

    if step_extract_bval_bvect_by_shells:

        path_b_vals = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwEffBval.txt')
        path_b_vects = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwGradVec.txt')

        print 'Separate b-vals and b-vect by shells: execution for subject {0}'.format(sj)

        if not safety_on:
            separate_shells_txt_path(path_b_vals, path_b_vects, prefix=sj,
                                     num_initial_dir_to_skip=1, num_shells=num_shells)

    if step_divide_dwi_image_by_shells:

        path_to_dwi = path_input_dwi    = os.path.join(root_ex_vivo_dwi, sj, 'DWI',
                                                       sj + '_DWI_cropped_and_slope_corrected.nii.gz')

        print 'Separate dwi by shells: execution for subject {0}'.format(sj)

        if not safety_on:
            separate_shells_dwi_path(path_to_dwi, prefix=sj, suffix='_DWI_shell_',
                                     num_initial_dir_to_skip=1, num_shells=num_shells)

    if step_dwi_analysis_nifty_fit_divided_by_shells:

        for sh in range(num_shells):

            # Analysis for each shell:

            path_input_dwi    = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_shell_' + str(sh) + '.nii.gz')

            path_input_bval   = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwEffBval_shell' + str(sh) + '.txt')
            path_input_bvect  = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwGradVec_shell' + str(sh) + '.txt')
            path_input_mask   = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')

            path_output_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit_divided_by_shells')
            path_output_dti    = os.path.join(path_output_folder, sj + '_v1map_shell' + str(sh) + '.nii.gz')
            path_output_rgb_map = os.path.join(path_output_folder, sj + '_rgbmap_shell' + str(sh) + '.nii.gz')
            path_output_adc_map = os.path.join(path_output_folder, sj + '_adcmap_shell' + str(sh) + '.nii.gz')
            path_output_fa_map = os.path.join(path_output_folder, sj + '_famap_shell' + str(sh) + '.nii.gz')

            # create the folder analysis_fit if nor present:
            cmd_0 = 'mkdir -p {0}'.format(path_output_folder)

            cmd = 'fit_dwi -source {0} -bval {1} -bvec {2}  -mask {3} ' \
                  '-v1map {4} -rgbmap {5} -mdmap {6} -famap {7}'.format(path_input_dwi,
                                                             path_input_bval,
                                                             path_input_bvect,
                                                             path_input_mask,
                                                             path_output_dti,
                                                             path_output_rgb_map,
                                                             path_output_adc_map,
                                                             path_output_fa_map)

            print '\nPerform DWI analysis by shells: execution for subject {0} and for shell {1}\n'.format(sj, sh)

            print cmd

            if not safety_on:
                os.system(cmd_0)
                os.system(cmd)

    if step_dwi_reorient_fit_divided_by_shells:

        for sh in range(num_shells):
            # copy the output for some new image!

            path_images_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit_divided_by_shells')

            path_analysis_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit_divided_by_shells')

            path_dti    = os.path.join(path_analysis_folder, sj + '_v1map_shell' + str(sh) + '.nii.gz')
            path_rgb_map = os.path.join(path_analysis_folder, sj + '_rgbmap_shell' + str(sh) + '.nii.gz')
            path_adc_map = os.path.join(path_analysis_folder, sj + '_adcmap_shell' + str(sh) + '.nii.gz')
            path_fa_map = os.path.join(path_analysis_folder, sj + '_famap_shell' + str(sh) + '.nii.gz')

            path_dti_new     = os.path.join(path_analysis_folder, sj + '_reoriented_v1map_shell' + str(sh) + '.nii.gz')
            path_rgb_map_new = os.path.join(path_analysis_folder, sj + '_reoriented_rgbmap_shell' + str(sh) + '.nii.gz')
            path_adc_map_new = os.path.join(path_analysis_folder, sj + '_reoriented_adcmap_shell' + str(sh) + '.nii.gz')
            path_fa_map_new  = os.path.join(path_analysis_folder, sj + '_reoriented_famap_shell' + str(sh) + '.nii.gz')

            list_paths = [path_dti, path_rgb_map, path_adc_map, path_fa_map]

            list_paths_new = [path_dti_new, path_rgb_map_new, path_adc_map_new, path_fa_map_new]

            print '\nReorient: execution for subject {0}.\n'.format(sj)

            for im, im_new in zip(list_paths, list_paths_new):
                cmd = ''' cp {0} {1};
                          fslorient -deleteorient {1};
                          fslswapdim {1} -z -y -x {1};
                          fslorient -setqformcode 1 {1};'''.format(im, im_new)
                print cmd
                if not safety_on:
                    os.system(cmd)

    ################
    # DRY CLEANERS #
    ################

    """ Erase un-useful things """
    if step_erase_unuseful_things:

        # list images to be erased:
        path_first_slice_dwi_extracted = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_first_slice_DWI.nii.gz')
        path_not_sloped_corrected = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped.nii.gz')

        # not reoriented analysis outcomes for nifty_fit:
        path_images_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit')
        path_dti    = os.path.join(path_images_folder, sj + '_v1map.nii.gz')
        path_rgb_map = os.path.join(path_images_folder, sj + '_rgbmap.nii.gz')
        path_adc_map = os.path.join(path_images_folder, sj + '_adcmap.nii.gz')
        path_fa_map = os.path.join(path_images_folder, sj + '_famap.nii.gz')
        #path_noddi = os.path.join(path_images_folder, sj + '_noddi.nii.gz')

        # not reoriented analysis, divided by shells:
        path_analysis_folder_divided_shells = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit_divided_by_shells')

        for sh in range(num_shells):

            path_dti    = os.path.join(path_analysis_folder, sj + '_v1map_shell' + str(sh) + '.nii.gz')
            path_rgb_map = os.path.join(path_analysis_folder, sj + '_rgbmap_shell' + str(sh) + '.nii.gz')
            path_adc_map = os.path.join(path_analysis_folder, sj + '_adcmap_shell' + str(sh) + '.nii.gz')
            path_fa_map = os.path.join(path_analysis_folder, sj + '_famap_shell' + str(sh) + '.nii.gz')

        # not reoriented analysis outcomes for fsl results:

        if verbose_on:
            print 'Erasing extra data for subject {0}'.format(sj)
