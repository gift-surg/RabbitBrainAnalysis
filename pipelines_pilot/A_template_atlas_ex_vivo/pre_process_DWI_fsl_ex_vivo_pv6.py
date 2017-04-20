"""
Process and align DWI in histological orientation.  https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/UsersGuide
"""
import os
from os.path import join as jph
import nibabel as nib
import numpy as np

from definitions import root_pilot_study
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data, \
    reproduce_slice_fourth_dimension_path
from tools.auxiliary.utils import print_and_run, adjust_header_from_transformations
from tools.correctors.slope_corrector import slope_corrector_path
from tools.auxiliary.reorient_data import reorient_bicomm2dwi, reorient_dwi2bicomm


def process_DWI_fsl_pv6(sj, control=None):

    print ' --- Pre process DWI FSL {} --- \n'.format(sj)

    # --- paths manager, general --- #

    root = jph(root_pilot_study, 'A_templ_atlas_ex_vivo')

    # path to DWI data subject

    pfi_dwi_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.nii.gz')
    # pfi_dwi_txt_data_original = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DWI.txt')

    if not os.path.isfile(pfi_dwi_original):
        msg = 'Input file subject {0} does not exists: \n{1}'.format(sj, pfi_dwi_original)
        raise IOError(msg)

    # if not os.path.isfile(pfi_dwi_txt_data_original):
    #     msg = 'Input data dfile subject {} does not exists'.format(sj)
    #     raise IOError(msg)

    # Paths to T1 images and roi mask of the same subject in histological coordinates:
    T1_in_histological_coordinates = jph(root, sj, 'all_modalities', sj + '_T1.nii.gz')
    T1_in_histological_coordinates_brain_mask = jph(root, sj, 'masks', sj + '_roi_mask.nii.gz')

    # check inputs:
    for ph in [T1_in_histological_coordinates, T1_in_histological_coordinates_brain_mask]:
        if not os.path.isfile(ph):
            raise IOError('File {} does not exist. Run pre-process T1 in vivo first'.format(ph))

    # --- Paths per step:  --- #

    # generate_output_folder
    outputs_folder = jph(root, sj, 'all_modalities', 'z_pre_process_DWI_fsl')

    # step_squeeze  in case the timepoints are in the 5th rather than the fourth dim
    pfi_dwi_squeezed = jph(outputs_folder, sj + '_DWI_squeezed.nii.gz')

    # step_extract_bval_bvect_slope
    # Output filenames (fn) are the default: 'DwDir.txt', 'DwEffBval.txt', 'DwGradVec.txt', 'VisuCoreDataSlope.txt'
    pfi_input_bvals   = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DwEffBval.txt')
    pfi_input_bvects  = jph(root_pilot_study, '0_original_data', 'ex_vivo', sj, 'DWI', sj + '_DwGradVec.txt')

    # check inputs:
    for ph in [pfi_input_bvals, pfi_input_bvects]:
        if not os.path.isfile(ph):
            raise IOError('File {} does not exist.'.format(ph))

    # step_extract_first_timepoint
    pfi_dwi_b0 = jph(outputs_folder, sj + '_DWI_first_timepoint.nii.gz')

    # step_grab_the_roi_mask
    pfi_T1_brain_skull_bicomm_reference = jph(root, sj, 'all_modalities', 'z_pre_process_T1',
                                              sj + '_brain_skull_only.nii.gz')
    pfi_T1_brain_skull_mask_bicomm_reference = jph(root, sj, 'all_modalities', 'z_pre_process_T1',
                                                   'brain_skull_mask_1305_on_' + sj + '.nii.gz')

    for ph in [pfi_T1_brain_skull_bicomm_reference, pfi_T1_brain_skull_mask_bicomm_reference]:
        if not os.path.isfile(ph):
            raise IOError('File {} does not exist. Run pre-process T1 in vivo first'.format(ph))

    pfi_T1_brain_skull_in_dwi_reference = os.path.join(outputs_folder, sj + '_T1_brain_skull_dwi_ref.nii.gz')
    pfi_T1_brain_skull_mask_in_dwi_reference = os.path.join(outputs_folder, sj + '_T1_brain_skull_dwi_ref_mask.nii.gz')

    pfi_warped_reoriented_bicom_T1_on_b0 = jph(outputs_folder, sj + '_reoriented_bicom_T1_on_b0_warped.nii.gz')
    pfi_affine_transformation_reoriented_bicom_T1_on_b0 = jph(outputs_folder,
                                                              sj + '_reoriented_bicom_T1_on_b0_aff.txt')

    pfi_roi_mask_dwi_orientation = jph(outputs_folder, sj + '_roi_mask_dwi_orientation.nii.gz')

    # step_dilate_mask
    dil_factor = 1
    pfi_roi_mask_dwi_orientation_dilated = jph(outputs_folder, sj + '_roi_mask_dwi_orientation_dil.nii.gz')

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

    # paths to results out of fsl:
    pfi_FA = jph(outputs_folder, name_for_analysis_fsl + '_FA.nii.gz')
    pfi_MD = jph(outputs_folder, name_for_analysis_fsl + '_MD.nii.gz')
    pfi_V1 = jph(outputs_folder, name_for_analysis_fsl + '_V1.nii.gz')
    pfi_S0 = jph(outputs_folder, name_for_analysis_fsl + '_S0.nii.gz')

    # paths to results out of fsl in bicommissural orientation
    pfi_FA_bicomm = jph(outputs_folder, 'bicomm_' + name_for_analysis_fsl + '_FA.nii.gz')
    pfi_MD_bicomm = jph(outputs_folder, 'bicomm_' + name_for_analysis_fsl + '_MD.nii.gz')
    pfi_V1_bicomm = jph(outputs_folder, 'bicomm_' + name_for_analysis_fsl + '_V1.nii.gz')
    pfi_S0_bicomm = jph(outputs_folder, 'bicomm_' + name_for_analysis_fsl + '_S0.nii.gz')

    pfi_FA_header_histo  = jph(outputs_folder, 'bicomm_header_histo_' + name_for_analysis_fsl + '_FA.nii.gz')
    pfi_MD_header_histo  = jph(outputs_folder, 'bicomm_header_histo_' + name_for_analysis_fsl + '_MD.nii.gz')
    pfi_V1_header_histo  = jph(outputs_folder, 'bicomm_header_histo_' + name_for_analysis_fsl + '_V1.nii.gz')
    pfi_S0_header_histo  = jph(outputs_folder, 'bicomm_header_histo_' + name_for_analysis_fsl + '_S0.nii.gz')

    # Path to corresponding T1 transformation from bicommissural to histological:
    pfi_aff_bicomm_to_histo_T1 = jph(root, sj, 'all_modalities', 'z_pre_process_T1', sj + '_transformation_to_histological_coordinates.txt')
    pfi_aff_bicomm_to_histo_T1_storage = jph(root, sj, 'all_modalities', 'z_pre_process_T1',
                                     'z_' + sj + '_transformation_to_histological_coordinates.txt')
    # paths to results out of fsl in histo orientation as T1
    pfi_S0_histo_as_T1 = jph(outputs_folder, 'histo_as_T1_' + name_for_analysis_fsl + '_S0.nii.gz')

    # Path to registration mask of the T1:
    pfi_registration_mask_in_histo_T1 = jph(root, sj, 'masks', sj + '_roi_registration_mask.nii.gz')
    if not os.path.exists(pfi_registration_mask_in_histo_T1):
        raise IOError

    # paths to results out of fsl in histo orientation as T1 readjusted
    pfi_S0_histo_as_T1_readjusted = jph(outputs_folder, 'histo_as_T1_readjusted_' + name_for_analysis_fsl + '_S0.nii.gz')

    # Small readjustments transformations
    pfi_aff_S0_histo_as_T1_readjusted = jph(outputs_folder, 'aff_transf_histo_on_T1_readjustment_' + sj + '_S0.txt')

    # Final transformation of the compositon main histo orientation as T1 o small readjustment
    pfi_final_aff_transf_bicomm_to_histo = jph(outputs_folder, 'aff_transf_final_bicomm_to_histo_' + sj + '_S0.txt')

    pfi_cropping_mask_for_the_V1 = jph(outputs_folder, sj + '_cropping_mask_V1_from_T1_roi_mask.nii.gz')

    # Final transformed
    pfi_FA_histo = jph(outputs_folder, 'histo_' + name_for_analysis_fsl + '_FA.nii.gz')
    pfi_MD_histo = jph(outputs_folder, 'histo_' + name_for_analysis_fsl + '_MD.nii.gz')
    pfi_V1_histo = jph(outputs_folder, 'histo_' + name_for_analysis_fsl + '_V1.nii.gz')
    pfi_S0_histo = jph(outputs_folder, 'histo_' + name_for_analysis_fsl + '_S0.nii.gz')

    # copied in the correct folder with the correct name:
    pfi_FA_final = jph(root, sj, 'all_modalities', sj + '_FA.nii.gz')
    pfi_MD_final = jph(root, sj, 'all_modalities', sj + '_MD.nii.gz')
    pfi_V1_final = jph(root, sj, 'all_modalities', sj + '_V1.nii.gz')
    pfi_S0_final = jph(root, sj, 'all_modalities', sj + '_S0.nii.gz')

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

        pass  # used for paravision 5 conversions.

    if control['step_extract_first_timepoint']:

        print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not control['safety_on']:
            nib_dwi = nib.load(pfi_dwi_squeezed)
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, pfi_dwi_b0)

    if control['step_grab_the_roi_mask']:

        # the roi mask is taken from the T1 processing, swapped in DWI reference and rigidly registered.

        # reorient to dwi:
        cmd1 = reorient_bicomm2dwi(pfi_T1_brain_skull_bicomm_reference, pfi_T1_brain_skull_in_dwi_reference)
        cmd2 = reorient_bicomm2dwi(pfi_T1_brain_skull_mask_bicomm_reference, pfi_T1_brain_skull_mask_in_dwi_reference)

        print_and_run(cmd1, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])

        # Register the swapped to the S0:

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly; '.format(
                    pfi_dwi_b0,
                    pfi_T1_brain_skull_in_dwi_reference,
                    pfi_affine_transformation_reoriented_bicom_T1_on_b0,
                    pfi_warped_reoriented_bicom_T1_on_b0)

        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                    pfi_dwi_b0,
                    pfi_T1_brain_skull_mask_in_dwi_reference,
                    pfi_affine_transformation_reoriented_bicom_T1_on_b0,
                    pfi_roi_mask_dwi_orientation)

        print '\nRegistration ROI mask (skull+brain): execution for subject {0}.\n'.format(sj)
        print_and_run(cmd_1, safety_on=control['safety_on'])
        print_and_run(cmd_2, safety_on=control['safety_on'])

    if control['step_dilate_mask']:

        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask_dwi_orientation, dil_factor, pfi_roi_mask_dwi_orientation_dilated)
        print_and_run(cmd, msg='Dilate mask ' + sj, safety_on=control['safety_on'])

    if control['step_cut_to_mask_dwi']:

        print '\nCutting newly-created ROI mask on the subject: execution for subject {0}.\n'.format(sj)
        if not control['safety_on']:
            cut_dwi_image_from_first_slice_mask_path(pfi_dwi_squeezed,
                                                     pfi_roi_mask_dwi_orientation_dilated,
                                                     pfi_dwi_cropped_to_roi)

    if control['step_correct_the_slope']:

        pass  # used for paravision 5.

    """ *** PHASE 2 - EDDY CURRENTS CORRECTION and analysis *** """

    if control['step_eddy_current_corrections']:

        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd, msg='\n Eddy currents correction: subject {}.\n'.format(sj), safety_on=control['safety_on'])
    else:
        pfi_dwi_eddy_corrected = pfi_dwi_slope_corrected

    if control['step_dwi_analysis_with_fsl']:

        here = os.getcwd()

        cmd0 = 'cd {}'.format(outputs_folder)
        cmd1 = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
              '-w --save_tensor -o {4}'.format(pfi_dwi_eddy_corrected,
                                               pfi_input_bvals,
                                               pfi_input_bvects,
                                               pfi_roi_mask_dwi_orientation_dilated,
                                               pfi_analysis_fsl)
        cmd2 = 'cd {}'.format(here)

        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, msg='DWI analysis: subject ' + sj, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])

    """ *** PHASE 3 - POST-PROCESSING *** """

    if control['step_orient_directions_bicomm']:

        # MOVE ALL RELEVANT RESULTS FROM DWI TO BICOMMISSURAL with HISTO HEADER:

        for pfi_in, pfi_out in zip([pfi_FA, pfi_MD, pfi_V1, pfi_S0],
                                   [pfi_FA_bicomm, pfi_MD_bicomm, pfi_V1_bicomm, pfi_S0_bicomm]):

            cmd = ''' cp {0} {1};
                      fslorient -deleteorient {1};
                      fslswapdim {1} -z -y -x {1};
                      fslorient -setqformcode 1 {1};'''.format(pfi_in, pfi_out)

            print_and_run(cmd, safety_on=control['safety_on'])

    if control['step_set_header_histo']:

        print '\nTAKE abs OF THE V1:'

        cmd = 'seg_maths {0} -abs {0}'.format(pfi_V1_bicomm)
        print_and_run(cmd, safety_on=control['safety_on'])

        for pfi_in, pfi_out in zip([pfi_FA_bicomm, pfi_MD_bicomm, pfi_V1_bicomm, pfi_S0_bicomm],
                       [pfi_FA_header_histo, pfi_MD_header_histo, pfi_V1_header_histo, pfi_S0_header_histo]):

            print 'Set header in histological for the bicommissural orientation: ' + pfi_in, pfi_out
            if not control['safety_on']:

                if sj == '1805' or sj == '2002' or sj == '2502':
                    pass  # no pre-adjustment (coherent with pre process T1)
                else:
                    theta = -np.pi / float(3)

                    adjust_header_from_transformations(pfi_in, pfi_out, theta=theta, trasl=(0, 0, 0))

    """ *** PHASE 3 - ORIENT RESULTS IN HISTOLOGICAL COORDINATES *** """

    if control['step_orient_histo']:  # orient histo pre-process -

        print '\nMOVING S0 FROM BICOMMISSURAL TO HISTOLOGICAL USING THE SAME TRANSFORMATION USED FOR T1'

        # if sj == '1805':
        #     os.system('cp {0} {1}'.format(pfi_aff_bicomm_to_histo_T1, pfi_aff_bicomm_to_histo_T1_storage))
        #     transf = np.loadtxt(pfi_aff_bicomm_to_histo_T1)
        #     transf_new = np.eye(4)
        #     transf_new[:3, :3] = transf[:3, :3]
        #     np.savetxt(pfi_aff_bicomm_to_histo_T1, transf_new)

        cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(
            T1_in_histological_coordinates,
            pfi_S0_header_histo,
            pfi_aff_bicomm_to_histo_T1,
            pfi_S0_histo_as_T1
        )

        print_and_run(cmd0, msg='Reorient bicomm to histo S0 ' + sj, safety_on=control['safety_on'])

        print '\nREGISTER S0 IN HISTOLOGICAL TO T1:'

        cmd1 = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -rigOnly '.format(
            T1_in_histological_coordinates,
            pfi_registration_mask_in_histo_T1,
            pfi_S0_histo_as_T1,
            pfi_registration_mask_in_histo_T1,
            pfi_aff_S0_histo_as_T1_readjusted,
            pfi_S0_histo_as_T1_readjusted,
        )

        print_and_run(cmd1, safety_on=control['safety_on'])

        print '\nCOMPOSE THE TWO OBTAINED TRANSFORMATION TO GET THE FINAL ONE: [(small adj) o (bicomm_2_histo)]'

        def compose_aff_transf_from_paths(pfi_left_aff, pfi_right_aff, pfi_final):

            if not os.path.exists(pfi_left_aff):
                raise IOError(pfi_left_aff)
            if not os.path.exists(pfi_right_aff):
                raise IOError(pfi_right_aff)

            left = np.loadtxt(pfi_left_aff)
            right = np.loadtxt(pfi_right_aff)
            np.savetxt(pfi_final, left.dot(right))

        if not control['safety_on']:
            compose_aff_transf_from_paths(pfi_aff_bicomm_to_histo_T1,  # small adj (NOTE reg resample takes the inverse)
                                          pfi_aff_S0_histo_as_T1_readjusted,  # main from bicomm 2 histo
                                          pfi_final_aff_transf_bicomm_to_histo)

        print '\nAPPLY THE FINAL OBTAINED TRANSFORMATION TO ALL THE RESULTS'

        for pfi_floating, pfi_res in zip([pfi_FA_header_histo, pfi_MD_header_histo, pfi_V1_header_histo, pfi_S0_header_histo],
                                         [pfi_FA_histo, pfi_MD_histo, pfi_V1_histo, pfi_S0_histo]):

            cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(
                T1_in_histological_coordinates,
                pfi_floating,
                pfi_final_aff_transf_bicomm_to_histo,
                pfi_res
            )
            print_and_run(cmd0, safety_on=control['safety_on'])

    if control['step_final_adjustment']:

        for pfi_sj in [pfi_FA_histo, pfi_MD_histo, pfi_V1_histo, pfi_S0_histo]:

            # CROP TO T1 MASK
            if 'V1' in pfi_sj:
                reproduce_slice_fourth_dimension_path(T1_in_histological_coordinates_brain_mask,
                                                      pfi_cropping_mask_for_the_V1, num_slices=3)
                cmd0 = 'seg_maths {0} -mul {1} {0}'.format(pfi_sj, pfi_cropping_mask_for_the_V1, pfi_sj)
                print_and_run(cmd0, safety_on=control['safety_on'])

            else:
                cmd0 = 'seg_maths {0} -mul {1} {0}'.format(pfi_sj, T1_in_histological_coordinates_brain_mask, pfi_sj)
                print_and_run(cmd0, safety_on=control['safety_on'])

            # REMOVE NAN
            cmd0 = 'seg_maths {0} -removenan {0}'.format(pfi_sj, T1_in_histological_coordinates_brain_mask, pfi_sj)
            print_and_run(cmd0, safety_on=control['safety_on'])

            # REMOVE NEGATIVE
            cmd0 = 'seg_maths {0} -thr {1} {0}'.format(pfi_sj, ' 0 ', pfi_sj)
            print_and_run(cmd0, safety_on=control['safety_on'])

    if control['step_bfc_b0']:

        print '\nBias field correction: subject {} S0 in DWI pipeline.\n'.format(sj)

        if not control['safety_on']:
            bias_field_correction(pfi_S0_histo, pfi_S0_histo,
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

        for pfi_original, pfi_copy in zip([pfi_FA_histo, pfi_MD_histo, pfi_V1_histo, pfi_S0_histo],
                                        [pfi_FA_final, pfi_MD_final, pfi_V1_final, pfi_S0_final]):

            cmd = 'cp {0} {1} '.format(pfi_original, pfi_copy)

            print_and_run(cmd, msg='Moving from original in the output folder to the new folder',
                          safety_on=control['safety_on'])

    """ *** PHASE 5 - ERASE THE INTERMEDIATE RESULTS *** """

    if control['delete_intermediate_steps']:

        cmd = 'rm -r {0} '.format(outputs_folder)
        print_and_run(cmd, msg='Erasing pre_process_DWI folder for subject {}.'.format(sj),
                      safety_on=control['safety_on'])
