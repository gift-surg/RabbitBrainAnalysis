"""
Based on nifty_fit, should be installed on the system before running the program.
"""
import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_dwi, root_ex_vivo_template
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data
from tools.parsers.parse_brukert_txt import parse_brukert_dwi_txt
from tools.correctors.slope_corrector import slope_corrector_path

# paths

# Controller
step_rename_original            = False
step_squeeze                    = False
step_extract_bval_bvect_slope   = False
step_extract_first_slice        = False
step_create_1d_layer_mask       = False
step_dilate_mask                = False
step_cut_to_mask_dwi            = False
step_correct_the_slope          = False
step_erase_unuseful_things      = False
step_dwi_analysis_nifty_fit     = False
step_reorient_nifty_fit         = True
step_dwi_analysis_fsl           = False

# only at the end of the process!
step_reorient                   = False

# safety, if on, plot only the command at terminal
safety_on = False


# Parameters
subjects = ['1201'] #, '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002']
dil_mask_factor = 5

# dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT
# http://www.cabiatl.com/Resources/Course/tutorial/html/dti.html
# http://www.mccauslandcenter.sc.edu/crnl/sw/tutorial/html/dti.html
# fit_dwi -source imput_image.nii.gz -bval b_values -bvec b_vectors -mask mask of the image -rgbmap file_dti_map -mdmap -famap

""" rename original """
if step_rename_original:
    for sj in subjects:

        path_dwi_nii_original = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        path_dwi_nii_saved_with_original_suffix = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_original.nii.gz')
        # save the original with the name _original.
        cmd = ' cp {0} {1} '.format(path_dwi_nii_original, path_dwi_nii_saved_with_original_suffix)
        print cmd
        if not safety_on:
            os.system(cmd)

""" SQUEEZE """
if step_squeeze:

    for sj in subjects:
        path_dwi_nii_squeezed = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')

        print '\n Squeeze for DWI images: execution for subject {0}.\n'.format(sj)
        print 'squeeze_image_from_path({0}, {1})'.format(path_dwi_nii_squeezed, path_dwi_nii_squeezed)

        if not safety_on:
            squeeze_image_from_path(path_dwi_nii_squeezed, path_dwi_nii_squeezed)


""" step_extract_bval_b_vect_slope """
if step_extract_bval_bvect_slope:

    for sj in subjects:

        path_dwi_txt_input = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.txt')

        print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)
        print 'parse_brukert_dwi_txt(path_dwi_txt_input, output_folder=os.path.dirname(path_dwi_txt_input))'

        if not safety_on:
            parse_brukert_dwi_txt(path_dwi_txt_input,
                                  output_folder=os.path.dirname(path_dwi_txt_input),
                                  prefix=sj + '_')

"""  Extract first slice of the DWI as a stand-alone image """
if step_extract_first_slice:
    for sj in subjects:

        path_oriented_as_dwi_1305_3d_template = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D.nii.gz')
        path_oriented_as_dwi_1305_3d_ciccione = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D_mask_fin_dil5.nii.gz')

        path_dwi = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        path_first_slice_dwi_extracted = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_first_slice_DWI.nii.gz')

        # Extract first slice and save as the fixed image - Keep the same header.

        print '\n extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            nib_dwi = nib.load(path_dwi)
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]

            nib_first_slice_dwi = set_new_data(nib.load(path_dwi), nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, path_first_slice_dwi_extracted)


""" Create the 1-time dimension DWI mask """
if step_create_1d_layer_mask:

    for sj in subjects:

        path_oriented_as_dwi_1305_3d_template = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D.nii.gz')
        path_oriented_as_dwi_1305_3d_ciccione = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D_mask_fin_dil5.nii.gz')

        # Register and propagate ciccione to first slice and save the registered ciccione - same header of the 3d image.

        print '\n Register and propagate ciccione to first slice and save the registered ciccione:' \
              ' execution for subject {0}.\n'.format(sj)

        path_affine_transformation_output = os.path.join(root_ex_vivo_dwi, sj, 'transformations', sj + '_on_unoriented_1305.txt')
        path_3d_warped_output = os.path.join(root_ex_vivo_dwi, 'zz_trash', sj +'_on_unoriented_1305.nii.gz')

        path_mask_output = os.path.join(root_ex_vivo_dwi, sj, 'masks',  sj +'_ciccione_roi_mask.nii.gz')

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly ; '.format(path_first_slice_dwi_extracted,
                                                                          path_oriented_as_dwi_1305_3d_template,
                                                                          path_affine_transformation_output,
                                                                          path_3d_warped_output)

        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_first_slice_dwi_extracted,
                                                                                      path_oriented_as_dwi_1305_3d_ciccione,
                                                                                      path_affine_transformation_output,
                                                                                      path_mask_output)

        print cmd_1
        print cmd_2

        if not safety_on:
            os.system(cmd_1+ cmd_2)


if step_dilate_mask:

    for sj in subjects:

        path_mask = os.path.join(root_ex_vivo_dwi, sj, 'masks',  sj +'_ciccione_roi_mask.nii.gz')
        cmd = 'seg_maths {0} -dil {1} {0}'.format(path_mask, dil_mask_factor)


""" cut the mask from the anatomical images - this will reduce the size of the DWI significantly """
if step_cut_to_mask_dwi:

    for sj in subjects:

        path_dwi_nii_input = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        path_3d_nii_mask_for_dwi = os.path.join(root_ex_vivo_dwi, sj, 'masks',  sj +'_ciccione_roi_mask.nii.gz')
        path_dwi_cropped_roi_result = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped.nii.gz')

        print '\nCutting newly-created ciccione mask on the subject: execution for subject {0}.\n'.format(sj)

        print 'cut_dwi_image_from_first_slice_mask_path({0},{1},{2})'.format(path_dwi_nii_input,
                                                                             path_3d_nii_mask_for_dwi,
                                                                             path_dwi_cropped_roi_result)

        if not safety_on:
            cut_dwi_image_from_first_slice_mask_path(path_dwi_nii_input,
                                                 path_3d_nii_mask_for_dwi,
                                                 path_dwi_cropped_roi_result)


""" Correct for the slopes on the trimmed images """
if step_correct_the_slope:

    for sj in subjects:

        path_slopes_txt_input = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_VisuCoreDataSlope.txt')

        path_3d_cropped_roi = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped.nii.gz')
        path_3d_sloped_cropped_result = os.path.join(root_ex_vivo_dwi, sj, 'DWI',
                                                     sj + '_DWI_cropped_and_slope_corrected.nii.gz')

        print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)
        print 'slope_corrector_path(path_slopes_txt_input, path_3d_cropped_roi, path_3d_sloped_cropped_result)'

        if not safety_on:
            slope_corrector_path(path_slopes_txt_input, path_3d_cropped_roi, path_3d_sloped_cropped_result)


""" Erase un-useful things """
if step_erase_unuseful_things:
    # path_first_slice_dwi_extracted = os.path.join(root_ex_vivo_dwi, sj, 'masks', sj + '_first_slice_DWI.nii.gz')
    pass


""" Perform the DWI analysi - nifty_fit """
if step_dwi_analysis_nifty_fit:

    for sj in subjects:

        path_input_dwi    = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_cropped_and_slope_corrected.nii.gz')
        path_input_bval   = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwEffBval.txt')
        path_input_bvect  = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DwGradVec.txt')
        path_input_mask   = os.path.join(root_ex_vivo_dwi, sj, 'masks',  sj +'_ciccione_roi_mask.nii.gz')

        path_output_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit')
        path_output_dti    = os.path.join(path_output_folder, sj + '_v1map.nii.gz')
        path_output_rgb_map = os.path.join(path_output_folder, sj + '_rgbmap.nii.gz')
        path_output_adc_map = os.path.join(path_output_folder, sj + '_adcmap.nii.gz')
        path_output_fa_map = os.path.join(path_output_folder, sj + '_famap.nii.gz')
        path_output_noddi = os.path.join(path_output_folder, sj + '_noddi.nii.gz')

        cmd = 'fit_dwi -source {0} -bval {1} -bvec {2} -mask {3} ' \
              '-v1map {4} -rgbmap {5} -mdmap {6} -famap {7} -nod {8}'.format(path_input_dwi,
                                                         path_input_bval,
                                                         path_input_bvect,
                                                         path_input_mask,
                                                         path_output_dti,
                                                         path_output_rgb_map,
                                                         path_output_adc_map,
                                                         path_output_fa_map,
                                                         path_output_noddi)

        print cmd

        if not safety_on:
            os.system(cmd)


""" REORIENT output - only after all the analysis!!! """
if step_reorient_nifty_fit:

    for sj in subjects:

        # copy the output for some new image! It is not idempotent!

        path_images_folder = os.path.join(root_ex_vivo_dwi, sj, 'analysis_fit')

        path_dti    = os.path.join(path_images_folder, sj + '_v1map.nii.gz')
        path_rgb_map = os.path.join(path_images_folder, sj + '_rgbmap.nii.gz')
        path_adc_map = os.path.join(path_images_folder, sj + '_adcmap.nii.gz')
        path_fa_map = os.path.join(path_images_folder, sj + '_famap.nii.gz')
        path_noddi = os.path.join(path_images_folder, sj + '_noddi.nii.gz')

        path_dti_new    = os.path.join(path_images_folder, sj + '_reoriented_v1map.nii.gz')
        path_rgb_map_new = os.path.join(path_images_folder, sj + '_reoriented_rgbmap.nii.gz')
        path_adc_map_new = os.path.join(path_images_folder, sj + '_reoriented_adcmap.nii.gz')
        path_fa_map_new = os.path.join(path_images_folder, sj + '_reoriented_famap.nii.gz')
        path_noddi_new = os.path.join(path_images_folder, sj + '_reoriented_noddi.nii.gz')

        list_paths = [path_dti, path_rgb_map, path_adc_map, path_fa_map, path_noddi]

        list_paths_new = [path_dti_new, path_rgb_map_new, path_adc_map_new, path_fa_map_new, path_noddi_new]

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        for im, im_new in zip(list_paths, list_paths_new):
            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(im, im_new)
            print cmd
            if not safety_on:
                os.system(cmd)

