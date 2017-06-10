"""
DWI processing in their original coordinate system.
"""
import os
from os.path import join as jph

import numpy as np

from tools.definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, \
    reproduce_slice_fourth_dimension_path, scale_y_value_and_trim, print_and_run, check_path
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
Cut mask B0
Correct the Slope
Eddy current correction
DWI analysis with FSL
Adjust dti-based modalities
Bfc B0
Save results

"""


def process_DWI_per_subject(sj, controller):

    print('\nProcessing DWI, subject {} started.\n'.format(sj))

    group = subject[sj][0][0]
    category = subject[sj][0][1]
    pfo_input_sj_DWI = jph(root_study_rabbits, '01_nifti', group, category, sj, sj + '_DWI')
    pfo_output_sj = jph(root_study_rabbits, 'A_data', group, category, sj)

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_DWI):
        raise IOError('Input folder DWI does not exist.')
    if not os.path.exists(pfo_output_sj):
        raise IOError('Output folder DWI does not exist.')

    # -- Generate intermediate and output folders:

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_DWI')

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    if controller['squeeze']:
        print('- squeeze {}'.format(sj))
        pfi_dwi = jph(pfo_input_sj_DWI, sj + '_DWI.nii.gz')
        assert check_path(pfi_dwi)
        squeeze_image_from_path(pfi_dwi, pfi_dwi)

    if controller['orient to standard']:
        print('- orient to standard {}'.format(sj))
        # DWI
        pfi_dwi_original = jph(pfo_input_sj_DWI, sj + '_DWI.nii.gz')
        assert check_path(pfi_dwi_original)
        pfi_dwi_std = jph(pfo_tmp, sj + '_DWI_to_std.nii.gz')
        cmd0 = 'fslreorient2std {0} {1}'.format(pfi_dwi_original, pfi_dwi_std)
        print_and_run(cmd0)
        set_translational_part_to_zero(pfi_dwi_std, pfi_dwi_std)
        # b0
        pfi_b0_original = jph(pfo_input_sj_DWI, sj + '_DWI_b0.nii.gz')
        assert check_path(pfi_b0_original)
        pfi_b0_std = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        cmd1 = 'fslreorient2std {0} {1}'.format(pfi_b0_original, pfi_b0_std)
        print_and_run(cmd1)
        set_translational_part_to_zero(pfi_b0_std, pfi_b0_std)

        if subject[sj][4][1]:
            scale_y_value_and_trim(pfi_dwi_std, pfi_dwi_std, squeeze_factor=2.218074656188605)
            scale_y_value_and_trim(pfi_b0_std, pfi_b0_std, squeeze_factor=2.218074656188605)

    if controller['register roi masks']:
        print('- register roi masks {}'.format(sj))
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        if subject[sj][0][1] in ['ex_vivo', 'op_skull']:
            pfi_sj_ref_coord_system = jph(root_study_rabbits, 'A_data', 'Utils', '1305', '1305_T1.nii.gz')
        elif subject[sj][0][1] == 'in_vivo':
            pfi_sj_ref_coord_system = jph(root_study_rabbits, 'A_data', 'Utils', '1504t1', '1504t1_T1.nii.gz')
        else:
            raise IOError('ex_vivo, in_vivo or op_skull only.')

        assert check_path(pfi_b0)
        assert check_path(pfi_sj_ref_coord_system)
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_on_' + sj + '_b0.txt')
        pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_on_' + sj + '_b0.nii.gz')
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} ; '.format(
            pfi_b0,
            pfi_sj_ref_coord_system,
            pfi_affine_transformation_ref_on_subject,
            pfi_3d_warped_ref_on_subject)
        print_and_run(cmd)

    if controller['propagate roi masks']:
        print('- propagate roi masks {}'.format(sj))
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        if subject[sj][0][1] in ['ex_vivo', 'op_skull']:
            pfi_reference_roi_mask = jph(root_study_rabbits, 'A_data', 'Utils', '1305', '1305_T1_roi_mask.nii.gz')
        elif subject[sj][0][1] == 'in_vivo':
            pfi_reference_roi_mask = jph(root_study_rabbits, 'A_data', 'Utils', '1504t1', '1504t1_roi_mask.nii.gz')
        else:
            raise IOError('ex_vivo, in_vivo or op_skull only.')
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_on_' + sj + '_b0.txt')
        assert check_path(pfi_b0)
        assert check_path(pfi_reference_roi_mask)
        assert check_path(pfi_affine_transformation_ref_on_subject)
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_b0,
            pfi_reference_roi_mask,
            pfi_affine_transformation_ref_on_subject,
            pfi_roi_mask)
        print_and_run(cmd)

    if controller['adjust mask']:
        print('- adjust mask {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_roi_mask)
        pfi_roi_mask_dil = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        dil_factor = subject[sj][4][0]
        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask,
                                                  dil_factor,
                                                  pfi_roi_mask_dil)
        print_and_run(cmd)

    if controller['cut mask dwi']:
        print('- cut mask dwi {}'.format(sj))
        pfi_dwi = jph(pfo_tmp, sj + '_DWI_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_dwi)
        assert check_path(pfi_roi_mask)
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        cut_dwi_image_from_first_slice_mask_path(pfi_dwi,
                                                 pfi_roi_mask,
                                                 pfi_dwi_cropped)

    if controller['cut mask b0']:
        print('- cut mask b0 {}'.format(sj))
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_b0)
        assert check_path(pfi_roi_mask)
        pfi_b0_cropped = jph(pfo_tmp, sj + '_b0_cropped.nii.gz')
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_b0, pfi_roi_mask, pfi_b0_cropped)
        print_and_run(cmd)

    if controller['correct slope']:
        print('- correct slope {}'.format(sj))
        # --
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        pfi_slope_txt = jph(pfo_input_sj_DWI, sj + '_DWI_slope.txt')
        assert check_path(pfi_dwi_cropped)
        assert check_path(pfi_slope_txt)
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        slopes = np.loadtxt(pfi_slope_txt)
        slope_corrector_path(slopes, pfi_dwi_cropped, pfi_dwi_slope_corrected)
        # --
        pfi_b0_cropped = jph(pfo_tmp, sj + '_b0_cropped.nii.gz')
        assert check_path(pfi_b0_cropped)
        pfi_b0_slope_corrected = jph(pfo_tmp, sj + '_b0_slope_corrected.nii.gz')
        slope_corrector_path(slopes[0], pfi_b0_cropped, pfi_b0_slope_corrected)

    if controller['eddy current']:
        print('- eddy current {}'.format(sj))
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        assert check_path(pfi_dwi_slope_corrected)
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd)
    else:
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        cmd = 'cp {0} {1} '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        print_and_run(cmd)

    if controller['fsl tensor fitting']:
        print('- fsl tensor fitting {}'.format(sj))
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        pfi_bvals = jph(pfo_input_sj_DWI, sj + '_DWI_DwEffBval.txt')
        pfi_bvects = jph(pfo_input_sj_DWI, sj + '_DWI_DwGradVec.txt')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_dwi_eddy_corrected)
        assert os.path.exists(pfi_bvals)
        assert os.path.exists(pfi_bvects)
        assert check_path(pfi_roi_mask)
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

    if controller['adjust dti-based mod']:
        print('- adjust dti-based modalities {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_roi_mask_4d = jph(pfo_mask, sj + '_b0_roi_mask_4d.nii.gz')
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')
        for pfi_mod in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            assert check_path(pfi_mod)

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
            
            cmd2 = 'seg_maths {0} -removenan {0}'.format(pfi_mod)
            print_and_run(cmd2)
            cmd3 = 'seg_maths {0} -thr {1} {0}'.format(pfi_mod, '0')
            print_and_run(cmd3)

    if controller['bfc b0']:
        print('- bfc b0 {}'.format(sj))
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_s0)
        assert check_path(pfi_roi_mask)
        bfc_param = subject[sj][3]
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

    if controller['create lesion mask']:
        print('- create lesion mask {}'.format(sj))
        pfi_s0_bfc = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0_bfc.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert check_path(pfi_s0_bfc)
        assert os.path.exists(pfi_roi_mask)
        pfi_lesion_mask = jph(pfo_mask, sj + '_b0_lesion_mask.nii.gz')
        percentile_lesion_mask_extractor(im_input_path=pfi_s0_bfc,
                                         im_output_path=pfi_lesion_mask,
                                         im_mask_foreground_path=pfi_roi_mask,
                                         percentiles=(10, 98),
                                         safety_on=False)

    if controller['create reg masks']:
        print('- create reg masks {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_lesion_mask = jph(pfo_mask, sj + '_b0_lesion_mask.nii.gz')
        assert os.path.exists(pfi_roi_mask)
        assert check_path(pfi_lesion_mask)
        pfi_registration_mask = jph(pfo_mask, sj + '_b0_reg_mask.nii.gz')
        cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask, pfi_lesion_mask,
                                                   pfi_registration_mask)  # until here seems correct.
        print_and_run(cmd)

    if controller['save results']:
        print('- save results {}'.format(sj))
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')
        for p in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            assert check_path(p)
        pfi_v1_new = jph(pfo_mod, sj + '_V1.nii.gz')
        pfi_s0_new = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_FA_new = jph(pfo_mod, sj + '_FA.nii.gz')
        pfi_MD_new = jph(pfo_mod, sj + '_MD.nii.gz')
        
        for a, b in zip([pfi_v1, pfi_s0, pfi_FA, pfi_MD], [pfi_v1_new, pfi_s0_new, pfi_FA_new, pfi_MD_new]):
            cmd = 'cp {0} {1}'.format(a, b)
            print_and_run(cmd)


def process_DWI_from_list(subj_list, controller):

    print '\n\n Processing DWI subjects in {} \n'.format(subj_list)
    for sj in subj_list:
        process_DWI_per_subject(sj, controller)


if __name__ == '__main__':
    print('process DWI, local run. ')

    controller_DWI = {'squeeze'               : False,
                      'orient to standard'    : False,
                      'register roi masks'    : False,
                      'propagate roi masks'   : False,
                      'adjust mask'           : False,
                      'cut mask dwi'          : False,
                      'cut mask b0'           : False,
                      'correct slope'         : False,
                      'eddy current'          : False,
                      'fsl tensor fitting'    : False,
                      'adjust dti-based mod'  : False,
                      'bfc b0'                : True,
                      'create lesion mask'    : False,
                      'create reg masks'      : False,
                      'save results'          : False}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['3108']  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    process_DWI_from_list(lsm.ls, controller_DWI)
    # execute_processing_DWI(controller_steps, rpa_dwi)
