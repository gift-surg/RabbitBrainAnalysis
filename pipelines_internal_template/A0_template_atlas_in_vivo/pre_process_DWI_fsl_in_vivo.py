import os
from os.path import join as jph
import nibabel as nib
import numpy as np

from definitions import root_pilot_study
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data, \
    reproduce_slice_fourth_dimension_path
from tools.auxiliary.utils import print_and_run
from tools.parsers.parse_bruker_txt import parse_bruker_dwi_txt
from tools.correctors.slope_corrector import slope_corrector_path
from tools.correctors.coordinates_header_coorectors import from_bicommissural_to_histological_header_orientation


def process_DWI_fsl(sj, control=None):

    print ' --- Pre process DWI FSL {} --- \n'.format(sj)

    # --- paths manager, general --- #

    root = jph(root_pilot_study, 'A_template_atlas_in_vivo')

    # path to DWI data subject

    pfi_dwi_original = jph(root_pilot_study, '0_original_data', 'in_vivo', sj, 'DWI', sj + '_DWI.nii.gz')
    pfi_dwi_txt_data_original = jph(root_pilot_study, '0_original_data', 'in_vivo', sj, 'DWI', sj + '_DWI.txt')

    if not os.path.isfile(pfi_dwi_original):
        msg = 'Input file subject {0} does not exists: \n{1}'.format(sj, pfi_dwi_original)
        raise IOError(msg)

    if not os.path.isfile(pfi_dwi_txt_data_original):
        msg = 'Input data dfile subject {} does not exists'.format(sj)
        raise IOError(msg)

    # preliminary template subject 0802:
    pfi_0802_template = jph(root, 'Utils', 'preliminary_template', 'in_vivo_template.nii.gz')
    pfi_0802_atlas = jph(root, 'Utils', 'preliminary_template', 'in_vivo_atlas_all_regions.nii.gz')

    if not os.path.isfile(pfi_0802_template):
        msg = 'Input file subject {} does not exists'.format(sj)
        raise IOError(msg)

    if not os.path.isfile(pfi_0802_atlas):
        msg = 'Input data dfile subject {} does not exists'.format(sj)
        raise IOError(msg)

    # --- Paths per step:  --- #
    # generate output folder
    pfo_outputs = jph(root, sj, 'all_modalities', 'z_pre_process_DWI_fsl')

    # step_squeeze  in case the timepoints are in the 5th rather than the fourth dim
    pfi_dwi_squeezed = jph(pfo_outputs, sj + '_DWI_squeezed.nii.gz')

    # step_extract_bval_bvect_slope
    # Output filenames (fn) are the default: 'DwDir.txt', 'DwEffBval.txt', 'DwGradVec.txt', 'VisuCoreDataSlope.txt'
    pfi_input_bvals   = os.path.join(pfo_outputs, sj + '_DwEffBval.txt')
    pfi_input_bvects  = os.path.join(pfo_outputs, sj + '_DwGradVec.txt')
    pfi_slopes_txt_file = jph(pfo_outputs, sj + '_VisuCoreDataSlope.txt')

    # step_correct_the_slope
    pfi_dwi_slope_corrected = jph(pfo_outputs, sj + '_DWI_slope_corrected.nii.gz')

    # step_eddy_current_corrections
    prefix_dwi_eddy_corrected = sj + '_DWI_fsl_eddy_corrected'
    pfi_dwi_eddy_corrected    = jph(pfo_outputs, prefix_dwi_eddy_corrected + '.nii.gz')

    # first slice and otsu thresholding to create the mask
    pfi_dwi_eddy_corrected_first_slice = jph(pfo_outputs, prefix_dwi_eddy_corrected + '_first_slice.nii.gz')
    pfi_dwi_eddy_corrected_mask = jph(pfo_outputs, prefix_dwi_eddy_corrected + '_mask.nii.gz')

    # step_dwi_analysis_with_fsl
    prefix_fsl_output = 'fsl_dtifit_'
    name_for_analysis_fsl = prefix_fsl_output + sj
    pfi_analysis_fsl = jph(pfo_outputs, name_for_analysis_fsl)

    suffix_results_to_keep = ['FA', 'MD', 'V1', 'S0']
    fn_results_to_keep = [name_for_analysis_fsl + '_' + suffix + '.nii.gz' for suffix in suffix_results_to_keep]

    # step_orient_histological
    pfi_affine_transformation_to_histological = jph(pfo_outputs, sj + '_transf_to_histological.txt')
    prefix_histo = 'histo_'

    # step_bfc_b0
    convergenceThreshold = 0.01
    maximumNumberOfIterations = (50, 40, 30, 20)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 200
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    """ *** PHASE 1 - DWI PRE-PROCESSING IN BICOMMISSURAL COORDINATES *** """

    if control['step_generate_output_folder']:

        cmd = 'mkdir -p ' + pfo_outputs
        print_and_run(cmd, msg='Generate output folder', safety_on=control['safety_on'])

    if control['step_squeeze']:

        print '\n Squeeze for DWI images: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            squeeze_image_from_path(pfi_dwi_original, pfi_dwi_squeezed, copy_anyway=True)

    if control['step_extract_bval_bvect_slope']:

        print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            parse_bruker_dwi_txt(pfi_dwi_txt_data_original,
                                 output_folder=pfo_outputs,
                                 prefix=sj + '_')

    if control['step_correct_the_slope']:

        print '\ncorrect for the slope: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            slope_corrector_path(pfi_slopes_txt_file, pfi_dwi_squeezed, pfi_dwi_slope_corrected,
                                 eliminate_consec_duplicates=True)

    """ *** PHASE 2 - EDDY CURRENTS CORRECTION and analysis *** """

    if control['step_eddy_current_corrections']:

        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd, msg='\n Eddy currents correction: subject {}.\n'.format(sj), safety_on=control['safety_on'])

    if control['step_get_roi_mask_in_dwi_coord']:

        print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not control['safety_on']:
            nib_dwi = nib.load(pfi_dwi_eddy_corrected)
            dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, pfi_dwi_eddy_corrected_first_slice)

            full_data = np.ones_like(nib_dwi.get_data()[..., 0]).astype(np.uint16)
            nib_dwi_full_volume = set_new_data(nib_dwi, full_data)
            nib.save(nib_dwi_full_volume, pfi_dwi_eddy_corrected_mask)

        '''
        cmd = 'seg_maths {0} -otsu {1} '.format(pfi_dwi_eddy_corrected_first_slice, pfi_dwi_eddy_corrected_mask)
        print_and_run(cmd, safety_on=control['safety_on'])

        cmd = 'seg_maths {0} -otsu {1} '.format(pfi_dwi_eddy_corrected_first_slice, pfi_dwi_eddy_corrected_mask)
        print_and_run(cmd, safety_on=control['safety_on'])

        cmd = 'seg_maths {0} -otsu {1} '.format(pfi_dwi_eddy_corrected_first_slice, pfi_dwi_eddy_corrected_mask)
        print_and_run(cmd, safety_on=control['safety_on'])
        '''

    if control['step_dwi_analysis_with_fsl']:

        here = os.getcwd()

        cmd0 = 'cd {}'.format(pfo_outputs)
        cmd1 = 'dtifit -k {0} -b {1} -r {2} ' \
              '-m {3} -w --save_tensor -o {4}'.format(pfi_dwi_eddy_corrected,
                                               pfi_input_bvals,
                                               pfi_input_bvects,
                                               pfi_dwi_eddy_corrected_mask,
                                               pfi_analysis_fsl)

        print cmd1
        cmd2 = 'cd {}'.format(here)

        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, msg='DWI analysis: subject ' + sj, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])

        pfi_V1 = jph(pfo_outputs, 'fsl_dtifit_' + sj + '_V1.nii.gz')
        cmd = 'seg_maths {0} -abs {0}'.format(pfi_V1)
        print_and_run(cmd, safety_on=control['safety_on'])

    """ *** PHASE 2bis - POST-PROCESSING *** """

    if control['step_orient_histological']:  # Orient in histological coordinate as the T1
        
        # Reference T1
        T1_in_histological_coordinates = jph(root, sj, 'all_modalities', sj + '_T1.nii.gz')

        # For each of the modality we are interested in do:
        for fn in fn_results_to_keep:  # fn : filename result to keep - input
            pfi_modality_from_fsl = jph(pfo_outputs, fn)
            pfi_modality_reoriented = jph(pfo_outputs, 'ori_3d_' + fn)

            # reorient modality
            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} x z -y {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_modality_from_fsl, pfi_modality_reoriented)
            print_and_run(cmd, safety_on=control['safety_on'])
            
            # apply the transformation in the header
            pfi_modality_reoriented_header = jph(pfo_outputs, 'ori_hd_' + fn)
            from_bicommissural_to_histological_header_orientation(pfi_modality_reoriented,
                                                                  pfi_modality_reoriented_header)
        # orient b0 with T1
        pfi_b0_reoriented_header = jph(pfo_outputs, 'ori_hd_fsl_dtifit_' + sj + '_S0.nii.gz')
        pfi_aff_trans_to_histo_coord = jph(pfo_outputs, 'to_histo_aff_mod_b0.txt')
        pfi_warped_to_histo_coord = jph(pfo_outputs, prefix_histo + 'fsl_dtifit_' + sj + '_S0.nii.gz')

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly ; '.format(T1_in_histological_coordinates,
                                                                        pfi_b0_reoriented_header,
                                                                        pfi_aff_trans_to_histo_coord,
                                                                        pfi_warped_to_histo_coord)

        print_and_run(cmd_1, safety_on=control['safety_on'])

        # For each of the modality we are interested in do:
        for fn in fn_results_to_keep:  # fn : filename result to keep - input
            pfi_modality_reoriented_header = jph(pfo_outputs, 'ori_hd_' + fn)
            pfi_warped_to_histo_coord = jph(pfo_outputs, prefix_histo + fn)
            cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} ; '.format(T1_in_histological_coordinates,
                                                                            pfi_modality_reoriented_header,
                                                                            pfi_aff_trans_to_histo_coord,
                                                                            pfi_warped_to_histo_coord)

            print_and_run(cmd_2, safety_on=control['safety_on'])

    if control['step_bfc_b0']:

        pfi_S0 = jph(pfo_outputs, prefix_histo + 'fsl_dtifit_' + sj + '_S0.nii.gz')

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

            pfi_original = jph(pfo_outputs, prefix_histo + fn)

            name_moved = sj + '_' + fn.split('.')[0][-2:] + '.nii.gz'
            pfi_moved = jph(root, sj, 'all_modalities', name_moved)

            cmd = 'cp {0} {1} '.format(pfi_original, pfi_moved)

            print_and_run(cmd, msg='Moving from original in the output folder to the new folder',
                          safety_on=control['safety_on'])

    """ *** PHASE 5 - ERASE THE INTERMEDIATE RESULTS *** """

    if control['delete_intermediate_steps']:

        cmd = 'rm -r {0} '.format(pfo_outputs)
        print_and_run(cmd, msg='Erasing pre_process_DWI folder for subject {}.'.format(sj),
                      safety_on=control['safety_on'])
