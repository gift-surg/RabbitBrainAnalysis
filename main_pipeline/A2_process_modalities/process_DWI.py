"""
DWI processing in their original coordinate system.
"""
import os
from os.path import join as jph
import pickle

import numpy as np
import nibabel as nib

from LABelsToolkit.tools.aux_methods.sanity_checks import check_path_validity
from LABelsToolkit.tools.aux_methods.utils_nib import set_new_data
from LABelsToolkit.main import LABelsToolkit

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from tools.auxiliary.reorient_images_header import orient2std
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, \
    reproduce_slice_fourth_dimension_path, scale_y_value_and_trim, print_and_run, set_new_data_path, \
    grab_a_timepoint_path
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.correctors.slope_corrector import slope_corrector_path

"""
Processing list for each DWI image acquired

Generate intermediate folders
Generate output folder
Squeeze
Orient to standard
Get roi masks -  steps
Adjust mask
Cut mask DWI
Cut mask S0
Correct the Slope
Eddy current correction
DWI analysis with FSL
Adjust dti-based modalities
Bfc S0
Save results
"""


def process_DWI_per_subject(sj, controller):

    print('\nProcessing DWI, subject {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    DWI_suffix = sj_parameters['names_architecture']['DWI']  # default is DWI

    study = sj_parameters['study']
    category = sj_parameters['category']
    pfo_input_sj_DWI = jph(root_study_rabbits, '02_nifti', study, category, sj, sj + '_' + DWI_suffix)
    pfo_output_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    if sj not in list_all_subjects(pfo_subjects_parameters):
        raise IOError('Subject parameters not known. Subject {}'.format(sj))
    if not os.path.exists(pfo_input_sj_DWI):
        raise IOError('Input folder DWI does not exist. Subject {}'.format(sj))
    if not os.path.exists(pfo_output_sj):
        raise IOError('Output folder DWI does not exist. Subject {}'.format(sj))

    # -- Generate intermediate and output folders:

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'masks')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_' + DWI_suffix)

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    if controller['squeeze']:
        print('- squeeze {}'.format(sj))
        pfi_dwi = jph(pfo_input_sj_DWI, '{}_{}.nii.gz'.format(sj, DWI_suffix))
        assert os.path.exists(pfi_dwi)
        squeeze_image_from_path(pfi_dwi, pfi_dwi)
        del pfi_dwi

    if controller['orient to standard']:
        print('- orient to standard {}'.format(sj))
        # DWI
        pfi_dwi_original = jph(pfo_input_sj_DWI, '{}_{}.nii.gz'.format(sj, DWI_suffix))
        assert check_path_validity(pfi_dwi_original)
        pfi_dwi_std = jph(pfo_tmp, '{}_DWI_to_std.nii.gz'.format(sj))
        orient2std(pfi_dwi_original, pfi_dwi_std)
        # S0
        if sj_parameters['b0_level'] == 0:
            pfi_S0_original = jph(pfo_input_sj_DWI, '{}_{}_S0.nii.gz'.format(sj, DWI_suffix))
        else:
            # create the time-point t and save its path under pfi_S0_original
            tp = sj_parameters['b0_level']
            pfi_DWI_original = jph(pfo_input_sj_DWI, '{}_{}.nii.gz'.format(sj, DWI_suffix))
            assert check_path_validity(pfi_DWI_original)
            pfi_S0_original = jph(pfo_tmp, '{0}_DWI_S0_tp{1}.nii.gz'.format(sj, tp))
            grab_a_timepoint_path(pfi_DWI_original, pfi_S0_original, tp)

        assert check_path_validity(pfi_S0_original)
        pfi_S0_std = jph(pfo_tmp, '{}_DWI_S0_to_std.nii.gz'.format(sj))
        orient2std(pfi_S0_original, pfi_S0_std)

        if sj_parameters['DWI_squashed']:
            scale_y_value_and_trim(pfi_dwi_std, pfi_dwi_std, squeeze_factor=2.218074656188605)
            scale_y_value_and_trim(pfi_S0_std, pfi_S0_std, squeeze_factor=2.218074656188605)
        del pfi_dwi_original, pfi_dwi_std, pfi_S0_original, pfi_S0_std

    if controller['create roi masks']:
        # Ideal pipeline uses the T1_roi_mask, that has been created before.
        # Not ideally some data have different orientation for each modality.
        # not ideally T1 has not been computed yet - not working in this case.

        # Path T1 mask
        pfi_sj_T1_roi_mask = jph(pfo_mask, '{}_T1_roi_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_sj_T1_roi_mask), 'Mask {} missing. Run T1 pipeline before'.format(pfi_sj_T1_roi_mask)

        # Conditional flags: mask creation options
        # can_resample_T1 = False  # Different modalities are in the same space. It is enough to resample T1.
        # need_to_register_mask = False  # Different modalities in different spaces. Pure resampling is not working!
        #
        # if isinstance(sj_parameters['angles'][0], list):
        #     need_to_register_mask = True
        # else:
        #     can_resample_T1 = True

        # # process:
        # if can_resample_T1:
        #     print('- Create roi masks {}'.format(sj))
        #     pfi_S0 = jph(pfo_tmp, sj + '_DWI_S0_to_std.nii.gz')
        #     pfi_affine_identity = jph(pfo_tmp, 'id.txt')
        #     np.savetxt(pfi_affine_identity, np.eye(4), fmt='%d')
        #     pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        #     cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
        #         pfi_S0,
        #         pfi_sj_T1_roi_mask,
        #         pfi_affine_identity,
        #         pfi_roi_mask)
        #     print_and_run(cmd)
        #     del pfi_S0, pfi_affine_identity, pfi_roi_mask, cmd
        #
        # elif need_to_register_mask:

        print('- Register roi masks {}'.format(sj))
        pfi_S0 = jph(pfo_tmp, sj + '_DWI_S0_to_std.nii.gz')
        assert os.path.exists(pfi_S0)

        pfi_T1          = jph(pfo_mod, '{}_T1.nii.gz'.format(sj))
        pfi_T1_roi_mask = jph(pfo_mask, '{}_T1_roi_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_T1), pfi_T1
        assert os.path.exists(pfi_T1_roi_mask), pfi_T1_roi_mask
        pfi_T1_hd_oriented = jph(pfo_tmp, sj + '_T1_hd_oriented_to_S0.nii.gz')
        pfi_T1_roi_mask_hd_oriented = jph(pfo_tmp, sj + '_T1_roi_mask_hd_oriented_to_S0.nii.gz')

        # check if the orientation angles are different for each modality:
        if isinstance(sj_parameters['angles'][0], list):
            # re-orient the T1 and the T1-mask on the S0 to better initialise the mask propagation.
            angles = sj_parameters['angles'][1]
            angle_parameter = angles[1]
            lt = LABelsToolkit()
            lt.header.apply_small_rotation(pfi_T1, pfi_T1_hd_oriented,
                                           angle=angle_parameter, principal_axis='pitch')
            lt.header.apply_small_rotation(pfi_T1_roi_mask, pfi_T1_roi_mask_hd_oriented,
                                           angle=angle_parameter, principal_axis='pitch')

        else:
            cmd1 = 'cp {0} {1}'.format(pfi_T1, pfi_T1_hd_oriented)
            cmd2 = 'cp {0} {1}'.format(pfi_T1_roi_mask, pfi_T1_roi_mask_hd_oriented)
            os.system(cmd1)
            os.system(cmd2)

        assert check_path_validity(pfi_T1_hd_oriented)
        assert check_path_validity(pfi_T1_roi_mask_hd_oriented)
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_on_' + sj + '_S0.txt')
        pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_on_' + sj + '_S0.nii.gz')
        cmd0 = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -rigOnly; '.format(
            pfi_S0,
            pfi_T1_hd_oriented,
            pfi_T1_roi_mask_hd_oriented,
            pfi_affine_transformation_ref_on_subject,
            pfi_3d_warped_ref_on_subject,
            num_cores_run)
        print_and_run(cmd0)

        print('- propagate roi masks {}'.format(sj))
        assert check_path_validity(pfi_affine_transformation_ref_on_subject)
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_S0,
            pfi_T1_roi_mask_hd_oriented,
            pfi_affine_transformation_ref_on_subject,
            pfi_roi_mask)
        print_and_run(cmd1)
        del pfi_S0, pfi_3d_warped_ref_on_subject, pfi_T1, pfi_T1_hd_oriented, pfi_T1_roi_mask, \
            pfi_T1_roi_mask_hd_oriented, pfi_affine_transformation_ref_on_subject, pfi_roi_mask, cmd0, cmd1

    if controller['adjust mask']:
        print('- adjust mask {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        assert check_path_validity(pfi_roi_mask)
        pfi_roi_mask_dil = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        dil_factor = sj_parameters['options_S0']['mask_dilation']
        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask,
                                                  dil_factor,
                                                  pfi_roi_mask_dil)
        print_and_run(cmd)
        del pfi_roi_mask, pfi_roi_mask_dil, dil_factor, cmd

    if controller['cut mask dwi']:
        print('- cut mask dwi {}'.format(sj))
        pfi_dwi = jph(pfo_tmp, sj + '_DWI_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        assert check_path_validity(pfi_dwi)
        assert check_path_validity(pfi_roi_mask)
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        cut_dwi_image_from_first_slice_mask_path(pfi_dwi,
                                                 pfi_roi_mask,
                                                 pfi_dwi_cropped)
        del pfi_dwi, pfi_roi_mask, pfi_dwi_cropped

    if controller['cut mask S0']:
        print('- cut mask S0 {}'.format(sj))
        pfi_S0 = jph(pfo_tmp, sj + '_DWI_S0_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        assert check_path_validity(pfi_S0)
        assert check_path_validity(pfi_roi_mask)
        pfi_S0_cropped = jph(pfo_tmp, sj + '_S0_cropped.nii.gz')
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_S0, pfi_roi_mask, pfi_S0_cropped)
        print_and_run(cmd)
        del pfi_S0, pfi_roi_mask, pfi_S0_cropped, cmd

    if controller['correct slope']:
        print('- correct slope {}'.format(sj))
        # --
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        pfi_slope_txt = jph(pfo_input_sj_DWI, '{}_{}_slope.txt'.format(sj, DWI_suffix))
        assert check_path_validity(pfi_dwi_cropped)
        assert check_path_validity(pfi_slope_txt)
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        slopes = np.loadtxt(pfi_slope_txt)
        slope_corrector_path(slopes, pfi_dwi_cropped, pfi_dwi_slope_corrected)
        # --
        pfi_S0_cropped = jph(pfo_tmp, sj + '_S0_cropped.nii.gz')
        assert check_path_validity(pfi_S0_cropped)
        pfi_S0_slope_corrected = jph(pfo_tmp, sj + '_S0_slope_corrected.nii.gz')
        slope_corrector_path(slopes[0], pfi_S0_cropped, pfi_S0_slope_corrected)
        del pfi_dwi_cropped, pfi_slope_txt, pfi_dwi_slope_corrected, slopes, pfi_S0_cropped, pfi_S0_slope_corrected

    if controller['eddy current']:
        print('- eddy current {}'.format(sj))
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        assert check_path_validity(pfi_dwi_slope_corrected)
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd)
        del pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected, cmd

    elif controller['fsl tensor fitting']:
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        cmd = 'cp {0} {1} '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd)
        del pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected, cmd
    else:
        pass

    if controller['fsl tensor fitting']:
        print('- fsl tensor fitting {}'.format(sj))
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')

        pfi_bvals = jph(pfo_input_sj_DWI, '{}_{}_DWI_DwEffBval.txt'.format(sj, DWI_suffix))
        pfi_bvects = jph(pfo_input_sj_DWI, '{}_{}_DWI_DwGradVec.txt'.format(sj, DWI_suffix))

        if isinstance(sj_parameters['b0_to_use_in_fsldti'], list):

            b0_tps_to_keep = sj_parameters['b0_to_use_in_fsldti']
            tag = str(b0_tps_to_keep).replace('[', '').replace(']', '').replace(',', '').replace(' ', '_')

            # out of the initial n uses only the one at the selected timepoint.
            bvals  = np.loadtxt(pfi_bvals)
            bvects = np.loadtxt(pfi_bvects)

            num_bzeros = np.sum(bvals == bvals[0])

            assert len(b0_tps_to_keep) < num_bzeros

            bvals_new = np.concatenate([[bvals[0], ] * len(b0_tps_to_keep) , bvals[num_bzeros:]])
            bvect_new = np.vstack([bvects[0, :].reshape(1, -1), ] * len(b0_tps_to_keep) + [bvects[num_bzeros:, :]])

            pfi_bvals_new = jph(pfo_tmp, '{}_DWI_DwEffBval_s0tp{}.txt'.format(sj, tag))
            pfi_bvects_new = jph(pfo_tmp, '{}_DWI_DwGradVec_s0tp{}.txt'.format(sj, tag))

            np.savetxt(pfi_bvals_new, bvals_new)
            np.savetxt(pfi_bvects_new, bvect_new)

            im_eddy_corrected = nib.load(pfi_dwi_eddy_corrected)

            x, y, z, t = im_eddy_corrected.shape

            data_only_one_tp = np.concatenate([im_eddy_corrected.get_data()[..., b0_tps_to_keep].reshape(x, y, z, -1),
                                               im_eddy_corrected.get_data()[..., num_bzeros:]] , axis=3)

            np.testing.assert_array_equal(data_only_one_tp.shape, [x, y, z, t - num_bzeros + len(b0_tps_to_keep)])

            im_eddy_corrected_only_one_b0_tp = set_new_data(im_eddy_corrected, data_only_one_tp)

            pfi_dwi_eddy_corrected_new = jph(pfo_tmp, '{}_DWI_eddy_s0tp{}.nii.gz'.format(sj, tag))
            nib.save(im_eddy_corrected_only_one_b0_tp, pfi_dwi_eddy_corrected_new)

            assert check_path_validity(pfi_dwi_eddy_corrected)
            assert os.path.exists(pfi_bvals)
            assert os.path.exists(pfi_bvects)
            assert check_path_validity(pfi_roi_mask)
            pfi_analysis_fsl = jph(pfo_tmp, 'fsl_fit_' + sj)
            here = os.getcwd()
            cmd0 = 'cd {}'.format(pfo_tmp)
            cmd1 = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
                   '-w --save_tensor -o {4}'.format(pfi_dwi_eddy_corrected_new,
                                                    pfi_bvals_new,
                                                    pfi_bvects_new,
                                                    pfi_roi_mask,
                                                    pfi_analysis_fsl)
            cmd2 = 'cd {}'.format(here)
            print_and_run(cmd0)
            print_and_run(cmd1)
            print_and_run(cmd2)

        else:
            assert check_path_validity(pfi_dwi_eddy_corrected)
            assert os.path.exists(pfi_bvals)
            assert os.path.exists(pfi_bvects)
            assert check_path_validity(pfi_roi_mask)
            pfi_analysis_fsl = jph(pfo_tmp, 'fsl_fit_' + sj)
            here = os.getcwd()
            cmd0 = 'cd {}'.format(pfo_tmp)
            cmd1 = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
                   '-w --save_tensor -o {4}'.format(pfi_dwi_eddy_corrected,
                                                    pfi_bvals,
                                                    pfi_bvects,
                                                    pfi_roi_mask,
                                                    pfi_analysis_fsl)
            cmd2 = 'cd {}'.format(here)
            print_and_run(cmd0)
            print_and_run(cmd1)
            print_and_run(cmd2)
        del pfi_dwi_eddy_corrected, pfi_bvals, pfi_bvects, pfi_roi_mask, pfi_analysis_fsl, cmd0, cmd1, cmd2

    if controller['adjust dti-based mod']:
        print('- adjust dti-based modalities {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        pfi_roi_mask_4d = jph(pfo_mask, sj + '_S0_roi_mask_4d.nii.gz')
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')

        cmd0, cmd1, cmd2 = None, None, None
        for pfi_mod in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            assert check_path_validity(pfi_mod)

            if 'V1' in pfi_mod:
                cmd0 = 'seg_maths {} -abs {}'.format(pfi_mod, pfi_mod)
                print_and_run(cmd0)
                reproduce_slice_fourth_dimension_path(pfi_roi_mask,
                                                      pfi_roi_mask_4d, num_slices=3)
                cmd1 = 'seg_maths {0} -mul {1} {0}'.format(pfi_mod, pfi_roi_mask_4d, pfi_mod)
                print_and_run(cmd1)
            else:
                cmd0 = 'seg_maths {0} -mul {1} {0}'.format(pfi_mod, pfi_roi_mask, pfi_mod)
                print_and_run(cmd0)
            
            cmd0 = 'seg_maths {0} -removenan {0}'.format(pfi_mod)
            print_and_run(cmd0)
            cmd1 = 'seg_maths {0} -thr {1} {0}'.format(pfi_mod, '0')
            print_and_run(cmd0)
        del pfi_roi_mask, pfi_roi_mask_4d, pfi_v1, pfi_s0, pfi_FA, pfi_MD, cmd0, cmd1, cmd2

    if controller['bfc S0']:
        print('- bfc S0 {}'.format(sj))
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        assert check_path_validity(pfi_s0)
        assert check_path_validity(pfi_roi_mask)
        set_new_data_path(pfi_target_im=pfi_s0,
                          pfi_image_where_the_new_data=pfi_roi_mask,
                          pfi_result=pfi_roi_mask)
        bfc_param = sj_parameters['bias_field_parameters']
        pfi_s0_bfc = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0_bfc.nii.gz')
        bias_field_correction(pfi_s0, pfi_s0_bfc,
                              pfi_mask=pfi_roi_mask,
                              prefix='',
                              convergenceThreshold=bfc_param[0],
                              maximumNumberOfIterations=bfc_param[1],
                              biasFieldFullWidthAtHalfMaximum=bfc_param[2],
                              wienerFilterNoise=bfc_param[3],
                              numberOfHistogramBins=bfc_param[4],
                              numberOfControlPoints=bfc_param[5],
                              splineOrder=bfc_param[6],
                              print_only=False)
        del pfi_s0, pfi_roi_mask, bfc_param, pfi_s0_bfc

    if controller['create lesion mask']:
        print('- create lesion mask {}'.format(sj))
        pfi_s0_bfc = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0_bfc.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        assert check_path_validity(pfi_s0_bfc)
        assert os.path.exists(pfi_roi_mask)
        pfi_lesion_mask = jph(pfo_mask, sj + '_S0_lesion_mask.nii.gz')
        percentile = sj_parameters['options_S0']['window_percentile']
        percentile_lesion_mask_extractor(im_input_path=pfi_s0_bfc,
                                         im_output_path=pfi_lesion_mask,
                                         im_mask_foreground_path=pfi_roi_mask,
                                         percentiles=percentile,
                                         safety_on=False)
        del pfi_s0_bfc, pfi_roi_mask, pfi_lesion_mask

    if controller['create reg masks']:
        print('- create reg masks {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        pfi_lesion_mask = jph(pfo_mask, sj + '_S0_lesion_mask.nii.gz')
        assert os.path.exists(pfi_roi_mask)
        assert check_path_validity(pfi_lesion_mask)
        pfi_registration_mask = jph(pfo_mask, sj + '_S0_reg_mask.nii.gz')
        cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask, pfi_lesion_mask,
                                                   pfi_registration_mask)  # until here seems correct.
        print_and_run(cmd)
        del pfi_roi_mask, pfi_lesion_mask, pfi_registration_mask, cmd

    if controller['save results']:
        print('- save results {}'.format(sj))
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')
        for p in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            assert check_path_validity(p)
        pfi_v1_new = jph(pfo_mod, sj + '_V1.nii.gz')
        pfi_s0_new = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_FA_new = jph(pfo_mod, sj + '_FA.nii.gz')
        pfi_MD_new = jph(pfo_mod, sj + '_MD.nii.gz')
        
        for a, b in zip([pfi_v1, pfi_s0, pfi_FA, pfi_MD], [pfi_v1_new, pfi_s0_new, pfi_FA_new, pfi_MD_new]):
            cmd = 'cp {0} {1}'.format(a, b)
            print_and_run(cmd)
        del pfi_v1, pfi_s0, pfi_FA, pfi_MD, pfi_v1_new, pfi_s0_new, pfi_FA_new, pfi_MD_new


def process_DWI_from_list(subj_list, controller):

    print '\n\n Processing DWI subjects in {} \n'.format(subj_list)
    for sj in subj_list:
        process_DWI_per_subject(sj, controller)


if __name__ == '__main__':
    print('process DWI, local run. ')

    controller_DWI = {'squeeze'               : True,
                      'orient to standard'    : True,
                      'create roi masks'      : True,
                      'adjust mask'           : True,
                      'cut mask dwi'          : True,
                      'cut mask S0'           : True,
                      'correct slope'         : True,
                      'eddy current'          : True,
                      'fsl tensor fitting'    : True,
                      'adjust dti-based mod'  : True,
                      'bfc S0'                : True,
                      'create lesion mask'    : True,
                      'create reg masks'      : True,
                      'save results'          : True}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    # lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    # lsm.input_subjects = ['12402']  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',

    lsm.input_subjects = ['125930']

    lsm.update_ls()

    process_DWI_from_list(lsm.ls, controller_DWI)
    # execute_processing_DWI(controller_steps, rpa_dwi)
