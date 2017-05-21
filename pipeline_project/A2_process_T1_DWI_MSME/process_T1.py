"""
T1 processing in their original coordinate system.
"""
import os
from os.path import join as jph
import numpy as np

from definitions import root_pilot_study_pantopolium
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from pipeline_project.U_utils.maps import subject
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero

"""
Processing list for each T1 of each subject:
(there are artefacts shared by multiple modalities, the group subdivision is meaningless. It must be done
subject-wise, using the map of parameters under U_Utils/maps)

Generate intermediate folder
Generate output folder
Orient to standard - fsl
Get mask - subject params.
Cut mask
Bias field correction
Compute registration and lesion mask

"""


def process_T1_per_subject(sj, pfo_input_sj_3D, pfo_output_sj, controller):

    print('\nProcessing T1 {} started.\n'.format(sj))

    # input sanity check:

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_3D):
        raise IOError('Input folder T1 does not exist.')

    # --  Generate intermediate and output folder

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_T1')

    os.system('mkdir -p {}'.format(pfo_output_sj))
    os.system('mkdir -p {}'.format(pfo_mod))
    os.system('mkdir -p {}'.format(pfo_segm))
    os.system('mkdir -p {}'.format(pfo_mask))
    os.system('mkdir -p {}'.format(pfo_tmp))

    if controller['orient to standard']:
        print('- orient to standard {}'.format(sj))
        pfi_input_original = jph(pfo_input_sj_3D, sj + '_3D.nii.gz')
        assert os.path.exists(pfi_input_original)
        pfi_std = jph(pfo_tmp, sj + '_to_std.nii.gz')
        cmd = 'fslreorient2std {0} {1}'.format(pfi_input_original,
                                               jph(pfo_tmp, sj + '_to_std.nii.gz'))
        os.system(cmd)
        set_translational_part_to_zero(pfi_std, pfi_std)

    if controller['threshold']:
        print('- threshold {}'.format(sj))
        assert os.path.exists(jph(pfo_input_sj_3D, sj + '_3D.nii.gz'))
        thr = subject[sj][3][0]
        cmd = 'seg_maths {0} -thr {1} {2}'.format(jph(pfo_tmp, sj + '_to_std.nii.gz'),
                                                  thr,
                                                  jph(pfo_tmp, sj + '_thr.nii.gz'))
        os.system(cmd)

    if controller['register roi masks']:
        print('- register roi masks {}'.format(sj))
        pfi_3d_thr = jph(pfo_tmp, sj + '_thr.nii.gz')
        pfi_1305 = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1.nii.gz')
        assert os.path.exists(pfi_3d_thr)
        assert os.path.exists(pfi_1305)
        pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
        pfi_3d_warped_1305_on_subject = jph(pfo_tmp, 'warp_1305_on_' + sj + '.nii.gz')
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} ; '.format(
            pfi_3d_thr,
            pfi_1305,
            pfi_affine_transformation_1305_on_subject,
            pfi_3d_warped_1305_on_subject)
        os.system(cmd)

    if controller['propagate roi masks']:
        print('- propagate roi masks {}'.format(sj))
        pfi_3d_thr = jph(pfo_tmp, sj + '_thr.nii.gz')
        pfi_1305_roi_mask = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1_roi_mask.nii.gz')
        pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
        assert os.path.exists(pfi_3d_thr)
        assert os.path.exists(pfi_1305_roi_mask)
        assert os.path.exists(pfi_affine_transformation_1305_on_subject)
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_3d_thr,
            pfi_1305_roi_mask,
            pfi_affine_transformation_1305_on_subject,
            pfi_roi_mask)
        os.system(cmd)

    if controller['adjust mask']:
        print('- adjust mask {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        assert os.path.exists(pfi_roi_mask)
        erosion_param = subject[sj][2][1]
        if erosion_param > 0:
            cmd = 'seg_maths {0} -ero {1} {2}'.format(pfi_roi_mask,
                                                      erosion_param,
                                                      pfi_roi_mask)
            os.system(cmd)

    if controller['cut masks']:
        print('- cut masks {}'.format(sj))
        pfi_3d_thr = jph(pfo_tmp, sj + '_thr.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        assert os.path.exists(pfi_3d_thr)
        assert os.path.exists(pfi_roi_mask)
        pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_3d_thr, pfi_roi_mask,
                                                  pfi_3d_cropped_roi)
        print '\nCutting newly-created ciccione mask on the subject: subject {0}.\n'.format(sj)
        os.system(cmd)

    if controller['step bfc']:
        print('- step bfc {}'.format(sj))
        pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
        assert os.path.exists(pfi_3d_cropped_roi)
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        bfc_param = subject[sj][3]
        bias_field_correction(pfi_3d_cropped_roi, pfi_3d_bias_field_corrected,
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
    else:
        pfi_3d_cropped_roi = jph(pfo_tmp, sj + '_cropped.nii.gz')
        assert os.path.exists(pfi_3d_cropped_roi)
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_3d_cropped_roi, pfi_3d_bias_field_corrected)
        os.system(cmd)

    if controller['create lesion mask']:
        print('- create lesion mask {}'.format(sj))
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        assert os.path.exists(pfi_3d_bias_field_corrected)
        assert os.path.exists(pfi_roi_mask)
        pfi_lesion_mask = jph(pfo_mask, sj + '_T1_lesion_mask.nii.gz')
        percentile_lesion_mask_extractor(im_input_path=pfi_3d_bias_field_corrected,
                                         im_output_path=pfi_lesion_mask,
                                         im_mask_foreground_path=pfi_roi_mask,
                                         percentiles=(15, 95),
                                         safety_on=False)

    if controller['create reg masks']:
        print('- create reg masks {}'.format(sj))
        pfi_roi_mask = jph(pfo_mask, sj + '_T1_roi_mask.nii.gz')
        pfi_lesion_mask = jph(pfo_mask, sj + '_T1_lesion_mask.nii.gz')
        assert os.path.exists(pfi_roi_mask)
        assert os.path.exists(pfi_roi_mask)
        pfi_registration_mask = jph(pfo_mask, sj + '_T1_reg_mask.nii.gz')
        cmd = 'seg_maths {0} -sub {1} {2} '.format(pfi_roi_mask, pfi_lesion_mask,
                                                       pfi_registration_mask)  # until here seems correct.
        os.system(cmd)

    if controller['save results']:
        print('- save results {}'.format(sj))
        pfi_3d_bias_field_corrected = jph(pfo_tmp, sj + '_bfc.nii.gz')
        assert os.path.exists(pfi_3d_bias_field_corrected)
        pfi_3d_final_destination = jph(pfo_mod, sj + '_T1.nii.gz')
        cmd = 'cp {0} {1}'.format(pfi_3d_bias_field_corrected, pfi_3d_final_destination)
        os.system(cmd)


def process_T1_per_group(controller, pfo_input_group_category, pfo_output_group_category, bypass_subjects=()):

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

        process_T1_per_subject(sj,
                               jph(pfo_input_group_category, sj, sj + '_3D'),
                               jph(pfo_output_group_category, sj),
                               controller)


def main_process_T1(controller,
                    process_T1_PTB_ex_skull=True,
                    process_T1_PTB_ex_vivo=True,
                    process_T1_PTB_in_vivo=True,
                    process_T1_PTB_op_skull=True,
                    process_T1_ACS_ex_vivo=True):

    print root_pilot_study_pantopolium
    root_nifti = jph(root_pilot_study_pantopolium, '01_nifti')
    root_data = jph(root_pilot_study_pantopolium, 'A_data')

    if process_T1_PTB_ex_skull:

        pfo_PTB_ex_skull = jph(root_nifti, 'PTB', 'ex_skull')
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')

        tuple_subjects = ()  # can force the input to a predefined input list of subjects if they exists.

        process_T1_per_group(controller, pfo_PTB_ex_skull, pfo_PTB_ex_skull_data, bypass_subjects=tuple_subjects)

    if process_T1_PTB_ex_vivo:

        pfo_PTB_ex_vivo = jph(root_nifti, 'PTB', 'ex_vivo')
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')

        tuple_subjects = ()

        process_T1_per_group(controller, pfo_PTB_ex_vivo, pfo_PTB_ex_vivo_data, bypass_subjects=tuple_subjects)

    if process_T1_PTB_in_vivo:

        pfo_PTB_in_vivo = jph(root_nifti, 'PTB', 'in_vivo')
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')

        tuple_subjects = ()

        process_T1_per_group(controller, pfo_PTB_in_vivo, pfo_PTB_in_vivo_data, bypass_subjects=tuple_subjects)

    if process_T1_PTB_op_skull:

        pfo_PTB_op_skull = jph(root_nifti, 'PTB', 'op_skull')
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')

        tuple_subjects = ()

        process_T1_per_group(controller, pfo_PTB_op_skull, pfo_PTB_op_skull_data, bypass_subjects=tuple_subjects)

    if process_T1_ACS_ex_vivo:

        pfo_ACS_ex_vivo = jph(root_nifti, 'ACS', 'ex_vivo')
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')

        tuple_subjects = ()

        process_T1_per_group(controller, pfo_ACS_ex_vivo, pfo_ACS_ex_vivo_data, bypass_subjects=tuple_subjects)


if __name__ == '__main__':

    if not os.path.isdir(root_pilot_study_pantopolium):
        raise IOError('Connect pantopolio!')

    controller_steps = {'orient to standard'  : False,
                        'threshold'           : False,
                        'register roi masks'  : False,
                        'propagate roi masks' : False,
                        'adjust mask'         : False,
                        'cut masks'           : False,
                        'step bfc'            : False,
                        'create lesion mask'  : True,
                        'create reg masks'    : True,
                        'save results'        : True}

    main_process_T1(controller_steps,
                    process_T1_PTB_ex_skull=False,
                    process_T1_PTB_ex_vivo=True,
                    process_T1_PTB_in_vivo=True,
                    process_T1_PTB_op_skull=False,
                    process_T1_ACS_ex_vivo=False
                    )
