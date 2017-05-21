"""
MSME processing in their original coordinate system
"""
import numpy as np
import os
from os.path import join as jph

from pipeline_project.U_utils.maps import subject
from definitions import root_pilot_study_pantopolium
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero

"""

Processing list for each MSME of each subject:

Generate intermediate folder
Generate output folder
squeeze
Orient to standard - fsl
Oversample
Extract first slice oversampled
Extract first slice normal
Get mask oversampled - subject params.
Downsample the mask

"""


def process_MSME_per_subject(sj, pfo_input_sj_MSME, pfo_output_sj, controller):
    print('\nProcessing DWI, subject {} started.\n'.format(sj))

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_MSME):
        raise IOError('Input folder DWI does not exist.')

    # -- Generate intermediate and output folders:

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_MSME')

    os.system('mkdir -p {}'.format(pfo_output_sj))
    os.system('mkdir -p {}'.format(pfo_mod))
    os.system('mkdir -p {}'.format(pfo_segm))
    os.system('mkdir -p {}'.format(pfo_mask))
    os.system('mkdir -p {}'.format(pfo_tmp))

    pfo_utils = jph(root_pilot_study_pantopolium, 'A_data', 'Utils')
    assert os.path.exists(pfo_utils)

    if controller['squeeze']:
        print('- squeeze {}'.format(sj))
        pfi_msme = jph(pfo_input_sj_MSME, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        pfi_msme_final = jph(pfo_output_sj, 'mod', sj + '_MSME.nii.gz')
        squeeze_image_from_path(pfi_msme, pfi_msme_final, copy_anyway=True)

    if controller['orient to standard']:
        print('- orient to standard {}'.format(sj))
        pfi_msme_final = jph(pfo_output_sj, 'mod', sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme_final)
        cmd = 'fslreorient2std {0} {0}'.format(pfi_msme_final)
        os.system(cmd)
        set_translational_part_to_zero(pfi_msme_final, pfi_msme_final)

    if controller['oversample']:
        print('- oversample {}'.format(sj))
        pfi_affine_identity = jph(pfo_utils, 'aff_id.txt')
        pfi_msme_original = jph(pfo_mod, sj + '_MSME.nii.gz')
        grid_size_param = subject[sj][5][0]
        if grid_size_param == 'low_res':  # this in the subject parameter!!
            pfi_resampling_grid = jph(pfo_utils, 'resampling_grid_low.nii.gz')
        elif grid_size_param == 'high_res':
            pfi_resampling_grid = jph(pfo_utils, 'resampling_grid_high.nii.gz')
        else:
            raise IOError
        assert os.path.exists(pfi_msme_original)
        assert os.path.exists(pfi_affine_identity)
        assert os.path.exists(pfi_resampling_grid)
        pfi_msme_upsampled = jph(pfo_output_sj, 'mod', sj + '_MSME_up.nii.gz')

        cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(pfi_resampling_grid,
                                                                           pfi_msme_original, 
                                                                           pfi_affine_identity,
                                                                           pfi_msme_upsampled)
        os.system(cmd0)
        cmd1 = 'seg_maths {0} -thr 0 {0}'.format(pfi_msme_upsampled)
        os.system(cmd1)

    if controller['extract first layers']:
        print('- extract first layers {}'.format(sj))
        pfi_msme_original = jph(pfo_output_sj, 'mod', sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme_original)
        pfi_msme_original_first_layer = jph(pfo_output_sj, 'mod', sj + '_MSME_1st.nii.gz')
        cmd0 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_original, pfi_msme_original_first_layer)
        os.system(cmd0)
        pfi_msme_upsampled = jph(pfo_output_sj, 'mod', sj + '_MSME_up.nii.gz')
        assert os.path.exists(pfi_msme_upsampled)
        pfi_msme_upsampled_first_layer = jph(pfo_output_sj, 'mod', sj + '_MSME_up_1st.nii.gz')
        cmd1 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_upsampled, pfi_msme_upsampled_first_layer)
        os.system(cmd1)

    if controller['register roi masks']:
        print('- register roi masks {}'.format(sj))
        pfi_msme_upsampled_first_layer = jph(pfo_output_sj, 'mod', sj + '_MSME_up_1st.nii.gz')
        pfi_1305 = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1.nii.gz')
        assert os.path.exists(pfi_msme_upsampled_first_layer)
        assert os.path.exists(pfi_1305)
        pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
        pfi_msme_warped_1305_on_subject = jph(pfo_tmp, 'warp_1305_on_' + sj + '.nii.gz')
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} ; '.format(
            pfi_msme_upsampled_first_layer,
            pfi_1305,
            pfi_affine_transformation_1305_on_subject,
            pfi_msme_warped_1305_on_subject)
        os.system(cmd)

    if controller['propagate roi masks']:
        print('- propagate roi masks {}'.format(sj))
        pfi_msme_upsampled_first_layer = jph(pfo_output_sj, 'mod', sj + '_MSME_up_1st.nii.gz')
        pfi_1305_roi_mask = jph(pfo_utils, '1305', '1305_T1_roi_mask.nii.gz')
        pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
        assert os.path.exists(pfi_msme_upsampled_first_layer)
        assert os.path.exists(pfi_1305_roi_mask)
        assert os.path.exists(pfi_affine_transformation_1305_on_subject)
        pfi_roi_mask = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_msme_upsampled_first_layer,
            pfi_1305_roi_mask,
            pfi_affine_transformation_1305_on_subject,
            pfi_roi_mask)

        os.system(cmd)
        

def process_MSME_per_group(controller, pfo_input_group_category, pfo_output_group_category, bypass_subjects=()):

    assert os.path.exists(pfo_input_group_category)
    assert os.path.exists(pfo_output_group_category)

    subj_list = np.sort(list(set(os.listdir(pfo_input_group_category)) - {'.DS_Store'}))

    # allow to force the subj_list to be the input tuple bypass subject, chosen by the user.
    if not bypass_subjects == ():

        if not set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n Processing MSME subjects  from {0} to {1} :\n {2}\n'.format(pfo_input_group_category,
                                                                            pfo_output_group_category,
                                                                            subj_list)
    for sj in subj_list:
        
        process_MSME_per_subject(sj,
                                 jph(pfo_input_group_category, sj, sj + '_MSME'),
                                 jph(pfo_output_group_category, sj),
                                 controller)


def main_process_DWI(controller,
                     process_MSME_PTB_ex_skull=False,
                     process_MSME_PTB_ex_vivo=False,
                     process_MSME_PTB_in_vivo=False,
                     process_MSME_PTB_op_skull=True,
                     process_MSME_ACS_ex_vivo=False):
    print root_pilot_study_pantopolium
    root_nifti = jph(root_pilot_study_pantopolium, '01_nifti')
    root_data = jph(root_pilot_study_pantopolium, 'A_data')

    if process_MSME_PTB_ex_skull:
        pfo_PTB_ex_skull = jph(root_nifti, 'PTB', 'ex_skull')
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')

        tuple_subjects = ()  # can force the input to a predefined input list of subjects if they exists.

        process_MSME_per_group(controller, pfo_PTB_ex_skull, pfo_PTB_ex_skull_data, bypass_subjects=tuple_subjects)

    if process_MSME_PTB_ex_vivo:
        pfo_PTB_ex_vivo = jph(root_nifti, 'PTB', 'ex_vivo')
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')

        tuple_subjects = ()

        process_MSME_per_group(controller, pfo_PTB_ex_vivo, pfo_PTB_ex_vivo_data, bypass_subjects=tuple_subjects)

    if process_MSME_PTB_in_vivo:
        pfo_PTB_in_vivo = jph(root_nifti, 'PTB', 'in_vivo')
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')

        tuple_subjects = ()

        process_MSME_per_group(controller, pfo_PTB_in_vivo, pfo_PTB_in_vivo_data, bypass_subjects=tuple_subjects)

    if process_MSME_PTB_op_skull:
        pfo_PTB_op_skull = jph(root_nifti, 'PTB', 'op_skull')
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')

        tuple_subjects = ()

        process_MSME_per_group(controller, pfo_PTB_op_skull, pfo_PTB_op_skull_data, bypass_subjects=tuple_subjects)

    if process_MSME_ACS_ex_vivo:
        pfo_ACS_ex_vivo = jph(root_nifti, 'ACS', 'ex_vivo')
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')

        tuple_subjects = ()

        process_MSME_per_group(controller, pfo_ACS_ex_vivo, pfo_ACS_ex_vivo_data, bypass_subjects=tuple_subjects)


if __name__ == '__main__':

    if not os.path.isdir(root_pilot_study_pantopolium):
        raise IOError('Connect pantopolio!')

    controller_steps = {'squeeze'              : True,
                        'orient to standard'   : True,
                        'oversample'           : True,
                        'extract first layers' : True,
                        'register roi masks'   : True,
                        'propagate roi masks'  : True
                        }

    main_process_DWI(controller_steps,
                     process_MSME_PTB_ex_skull=False,
                     process_MSME_PTB_ex_vivo=True,
                     process_MSME_PTB_in_vivo=False,
                     process_MSME_PTB_op_skull=False,
                     process_MSME_ACS_ex_vivo=False
                     )
