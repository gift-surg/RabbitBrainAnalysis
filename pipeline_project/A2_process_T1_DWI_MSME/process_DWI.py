"""
DWI processing in their original coordinate system.
"""
import os
from os.path import join as jph

import numpy as np

from pipeline_project.U_utils.maps import subject
from definitions import root_pilot_study_pantopolium
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data, \
    reproduce_slice_fourth_dimension_path
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


def process_DWI_per_subject(sj, pfo_input_sj_DWI, pfo_output_sj, controller):

    print('\nProcessing DWI, subject {} started.\n'.format(sj))

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_DWI):
        raise IOError('Input folder DWI does not exist.')

    # -- Generate intermediate and output folders:

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_DWI')

    os.system('mkdir -p {}'.format(pfo_output_sj))
    os.system('mkdir -p {}'.format(pfo_mod))
    os.system('mkdir -p {}'.format(pfo_segm))
    os.system('mkdir -p {}'.format(pfo_mask))
    os.system('mkdir -p {}'.format(pfo_tmp))

    if controller['squeeze']:
        pfi_dwi = jph(pfo_input_sj_DWI, sj + '_DWI.nii.gz')
        assert os.path.exists(pfi_dwi)
        squeeze_image_from_path(pfi_dwi, pfi_dwi)

    if controller['orient to standard']:
        cmd0 = 'fslreorient2std {0} {1}'.format(jph(pfo_input_sj_DWI, sj + '_DWI.nii.gz'),
                                                jph(pfo_tmp, sj + '_DWI_to_std.nii.gz'))
        os.system(cmd0)
        cmd1 = 'fslreorient2std {0} {1}'.format(jph(pfo_input_sj_DWI, sj + '_DWI_b0.nii.gz'),
                                                jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz'))
        os.system(cmd1)

    if controller['register roi masks']:
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        pfi_1305 = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1.nii.gz')
        pfi_affine_transformation_1305_on_subject = jph(pfo_output_sj, 'z_tmp', 'aff_1305_on_' + sj + '_b0.txt')
        pfi_3d_warped_1305_on_subject = jph(pfo_tmp, 'warp_1305_on_' + sj + '_b0.nii.gz')
        assert os.path.exists(pfi_b0)
        assert os.path.exists(pfi_1305)
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} ; '.format(
            pfi_b0,
            pfi_1305,
            pfi_affine_transformation_1305_on_subject,
            pfi_3d_warped_1305_on_subject)
        os.system(cmd)

    if controller['propagate roi masks']:
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        pfi_1305_roi_mask = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1_roi_mask.nii.nii.gz')
        pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '_b0.txt')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert os.path.exists(pfi_b0)
        assert os.path.exists(pfi_1305_roi_mask)
        assert os.path.exists(pfi_affine_transformation_1305_on_subject)
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_b0,
            pfi_1305_roi_mask,
            pfi_affine_transformation_1305_on_subject,
            pfi_roi_mask)
        os.system(cmd)

    if controller['adjust mask']:
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert os.path.exists(pfi_roi_mask)
        pfi_roi_mask_dil = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        dil_factor = subject[sj][4][0]
        cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_roi_mask,
                                                  dil_factor,
                                                  pfi_roi_mask_dil)
        os.system(cmd)

    if controller['cut mask dwi']:
        pfi_dwi = jph(pfo_tmp, sj + '_DWI_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        assert os.path.exists(pfi_dwi)
        assert os.path.exists(pfi_roi_mask)
        cut_dwi_image_from_first_slice_mask_path(pfi_dwi,
                                                 pfi_roi_mask,
                                                 pfi_dwi_cropped)

    if controller['cut mask b0']:
        pfi_b0 = jph(pfo_tmp, sj + '_DWI_b0_to_std.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_b0_cropped = jph(pfo_tmp, sj + '_b0_cropped.nii.gz')
        assert os.path.exists(pfi_b0)
        assert os.path.exists(pfi_roi_mask)
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_b0, pfi_roi_mask, pfi_b0_cropped)
        os.system(cmd)

    if controller['correct slope']:
        pfi_dwi_cropped = jph(pfo_tmp, sj + '_DWI_cropped.nii.gz')
        pfi_slope_txt = jph(pfo_input_sj_DWI, sj + '_DWI_slope.txt')
        assert os.system(pfi_dwi_cropped)
        assert os.system(pfi_slope_txt)
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        slope_corrector_path(pfi_slope_txt, pfi_dwi_cropped, pfi_dwi_slope_corrected)

    if controller['eddy current']:
        pfi_dwi_slope_corrected = jph(pfo_tmp, sj + '_DWI_slope_corrected.nii.gz')
        assert os.path.exists(pfi_dwi_slope_corrected)
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_dwi_slope_corrected, pfi_dwi_eddy_corrected)
        os.system(cmd)

    if controller['fsl tensor fitting']:
        pfi_dwi_eddy_corrected = jph(pfo_tmp, sj + '_DWI_eddy.nii.gz')
        pfi_bvals = jph(pfo_input_sj_DWI, sj + '_DWI_DwBval.txt')
        pfi_bvects = jph(pfo_input_sj_DWI, sj + '_DWI_DwGradVec.txt')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
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

        os.system(cmd0)
        os.system(cmd1)
        os.system(cmd2)

    if controller['adjust dti-based modalities']:

        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_roi_mask_4d = jph(pfo_mask, sj + '_b0_roi_mask_4d.nii.gz')
        
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')

        for pfi_mod in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            
            assert os.path.exists(pfi_mod)

            if 'V1' in pfi_mod:
                cmd0 = 'seg_maths {} -abs {}'.format(pfi_mod, pfi_mod)
                os.system(cmd0)
                reproduce_slice_fourth_dimension_path(pfi_roi_mask,
                                                      pfi_roi_mask_4d, num_slices=3)
                cmd1 = 'seg_maths {0} -mul {1} {0}'.format(pfi_mod, pfi_roi_mask_4d, pfi_mod)
                os.system(cmd1)
            else:
                cmd0 = 'seg_maths {0} -mul {1} {0}'.format(pfi_mod, pfi_roi_mask, pfi_mod)
                os.system(cmd0)
            
            cmd2 = 'seg_maths {0} -removenan {0}'.format(pfi_mod)
            os.system(cmd2)
            cmd3 = 'seg_maths {0} -thr {1} {0}'.format(pfi_mod, '0')
            os.system(cmd3)

    if controller['bfc b0']:
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        bfc_param = subject[sj][3]
        pfi_s0_bfc = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0_bfc.nii.gz')

        assert os.path.exists(pfi_s0)

        bias_field_correction(pfi_s0, pfi_s0_bfc,
                              pfi_mask=None,
                              prefix='',
                              convergenceThreshold=bfc_param[0],
                              maximumNumberOfIterations=bfc_param[1],
                              biasFieldFullWidthAtHalfMaximum=bfc_param[2],
                              wienerFilterNoise=bfc_param[3],
                              numberOfHistogramBins=bfc_param[4],
                              numberOfControlPoints=bfc_param[5],
                              splineOrder=bfc_param[6],
                              print_only=False)

    if controller['save results']:
        pfi_v1 = jph(pfo_tmp, 'fsl_fit_' + sj + '_V1.nii.gz')
        pfi_s0 = jph(pfo_tmp, 'fsl_fit_' + sj + '_S0.nii.gz')
        pfi_FA = jph(pfo_tmp, 'fsl_fit_' + sj + '_FA.nii.gz')
        pfi_MD = jph(pfo_tmp, 'fsl_fit_' + sj + '_MD.nii.gz')
        
        for p in [pfi_v1, pfi_s0, pfi_FA, pfi_MD]:
            assert os.path.exists(p)

        pfi_v1_new = jph(pfo_mod, sj + '_V1.nii.gz')
        pfi_s0_new = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_FA_new = jph(pfo_mod, sj + '_FA.nii.gz')
        pfi_MD_new = jph(pfo_mod, sj + '_MD.nii.gz')
        
        for a, b in zip([pfi_v1, pfi_s0, pfi_FA, pfi_MD], [pfi_v1_new, pfi_s0_new, pfi_FA_new, pfi_MD_new]):
            cmd = 'cp {0} {1}'.format(a, b)
            os.system(cmd)


def process_DWI_per_group(controller, pfo_input_group_category, pfo_output_group_category, bypass_subjects=()):
    assert os.path.exists(pfo_input_group_category)
    assert os.path.exists(pfo_output_group_category)

    subj_list = np.sort(list(set(os.listdir(pfo_input_group_category)) - {'.DS_Store'}))

    # allow to force the subj_list to be the input tuple bypass subject, chosen by the user.
    if not bypass_subjects == ():

        if not set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n Processing T1 subjects  from {0} to {1} :\n {2}\n'.format(pfo_input_group_category,
                                                                          pfo_output_group_category,
                                                                          subj_list)
    for sj in subj_list:
        process_DWI_per_subject(sj,
                               jph(pfo_input_group_category, sj, sj + '_DWI'),
                               jph(pfo_output_group_category, sj),
                               controller)


def main_process_DWI(controller,
                     process_DWI_PTB_ex_skull=False,
                     process_DWI_PTB_ex_vivo=False,
                     process_DWI_PTB_in_vivo=False,
                     process_DWI_PTB_op_skull=True,
                     process_DWI_ACS_ex_vivo=False):
    
    print root_pilot_study_pantopolium
    root_nifti = jph(root_pilot_study_pantopolium, '01_nifti')
    root_data = jph(root_pilot_study_pantopolium, 'A_data')

    if process_DWI_PTB_ex_skull:
        pfo_PTB_ex_skull = jph(root_nifti, 'PTB', 'ex_skull')
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')

        tuple_subjects = ()  # can force the input to a predefined input list of subjects if they exists.

        process_DWI_per_group(controller, pfo_PTB_ex_skull, pfo_PTB_ex_skull_data, bypass_subjects=tuple_subjects)

    if process_DWI_PTB_ex_vivo:
        pfo_PTB_ex_vivo = jph(root_nifti, 'PTB', 'ex_vivo')
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')

        tuple_subjects = ()

        process_DWI_per_group(controller, pfo_PTB_ex_vivo, pfo_PTB_ex_vivo_data, bypass_subjects=tuple_subjects)

    if process_DWI_PTB_in_vivo:
        pfo_PTB_in_vivo = jph(root_nifti, 'PTB', 'in_vivo')
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')

        tuple_subjects = ()

        process_DWI_per_group(controller, pfo_PTB_in_vivo, pfo_PTB_in_vivo_data, bypass_subjects=tuple_subjects)

    if process_DWI_PTB_op_skull:
        pfo_PTB_op_skull = jph(root_nifti, 'PTB', 'op_skull')
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')

        tuple_subjects = ()

        process_DWI_per_group(controller, pfo_PTB_op_skull, pfo_PTB_op_skull_data, bypass_subjects=tuple_subjects)

    if process_DWI_ACS_ex_vivo:
        pfo_ACS_ex_vivo = jph(root_nifti, 'ACS', 'ex_vivo')
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')

        tuple_subjects = ()

        process_DWI_per_group(controller, pfo_ACS_ex_vivo, pfo_ACS_ex_vivo_data, bypass_subjects=tuple_subjects)

if __name__ == '__main__':

    if not os.path.isdir('/Volumes/sebastianof/rabbits/'):
        raise IOError('Connect pantopolio!')

    controller_steps = {'squeeze'             : True,
                        'orient to standard'  : True,
                        'threshold'           : True,
                        'register roi masks'  : True,
                        'propagate roi masks' : True,
                        'adjust mask'         : True,
                        'cut masks'           : True,
                        'step bfc'            : True,
                        'create lesion mask'  : True,
                        'create reg masks'    : True,
                        'save results'        : True}

    main_process_DWI(controller_steps,
                     process_DWI_PTB_ex_skull=False,
                     process_DWI_PTB_ex_vivo=False,
                     process_DWI_PTB_in_vivo=False,
                     process_DWI_PTB_op_skull=True,
                     process_DWI_ACS_ex_vivo=False
                     )

