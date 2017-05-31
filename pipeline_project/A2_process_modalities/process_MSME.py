"""
MSME processing in their original coordinate system
"""
import os
from os.path import join as jph

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero
from tools.auxiliary.squeezer import squeeze_image_from_path

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


def process_MSME_per_subject(sj, controller):
    print('\nProcessing MSME, subject {} started.\n'.format(sj))

    group = subject[sj][0][0]
    category = subject[sj][0][1]
    pfo_input_sj = jph(root_study_rabbits, '01_nifti', group, category, sj)
    pfo_output_sj = jph(root_study_rabbits, 'A_data', group, category, sj)

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj):
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

    pfo_utils = jph(root_study_rabbits, 'A_data', 'Utils')
    assert os.path.exists(pfo_utils)

    if controller['squeeze']:
        print('- Processing MSME: squeeze {}'.format(sj))
        pfi_msme = jph(pfo_input_sj, sj + '_MSME', sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        pfi_msme_final = jph(pfo_output_sj, 'mod', sj + '_MSME.nii.gz')
        squeeze_image_from_path(pfi_msme, pfi_msme_final, copy_anyway=True)

    if controller['orient to standard']:
        print('- Processing MSME: orient to standard {}'.format(sj))
        pfi_msme_final = jph(pfo_mod, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme_final)
        cmd = 'fslreorient2std {0} {0}'.format(pfi_msme_final)
        os.system(cmd)
        set_translational_part_to_zero(pfi_msme_final, pfi_msme_final)

    if controller['extract first timepoint']:
        print('- Processing MSME: extract first layers {}'.format(sj))
        pfi_msme = jph(pfo_mod, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        pfi_msme_original_first_layer = jph(pfo_mod, sj + '_MSME_tp0.nii.gz')
        cmd0 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme, pfi_msme_original_first_layer)
        os.system(cmd0)
    #
    # if controller['extract the mask']:
    #     print('- Processing MSME: extract mask {}'.format(sj))
    #     # --- Resampling on the S0:
    #     pfi_affine_identity = jph(pfo_utils, 'aff_id.txt')
    #     pfi_msme_tp0 = jph(pfo_mod, sj + '_MSME_tp0.nii.gz')
    #     pfi_s0 = jph(pfo_output_sj, 'mod', sj + '_S0.nii.gz')
    #     assert os.path.exists(pfi_msme_tp0)
    #     assert os.path.exists(pfi_affine_identity)
    #     assert os.path.exists(pfi_s0)
    #     # Create ad hoc resampling grid from S0:
    #     pfi_resampling_grid = jph(pfo_tmp, sj + '_resampling_grid.nii.gz')
    #     im_s0 = nib.load(pfi_s0)
    #     im_grid = set_new_data(im_s0, np.zeros_like(im_s0.get_data()))
    #     nib.save(im_grid, filename=pfi_resampling_grid)
    #     # Resample on the new grid:
    #     assert os.path.exists(pfi_resampling_grid)
    #     pfi_msme_tp0_up = jph(pfo_output_sj, 'mod', sj + '_MSME_tp0_up.nii.gz')
    #     cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(pfi_resampling_grid,
    #                                                                        pfi_msme_tp0,
    #                                                                        pfi_affine_identity,
    #                                                                        pfi_msme_tp0_up)
    #     os.system(cmd0)
    #     cmd1 = 'seg_maths {0} -thr 0 {0}'.format(pfi_msme_tp0_up)
    #     os.system(cmd1)
    #     # -- register 1305 on the up-sampled first layer MSME:
    #     pfi_1305 = jph(root_study_pantopolium, 'A_data', 'Utils', '1305', '1305_T1.nii.gz')
    #     assert os.path.exists(pfi_1305)
    #     pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
    #     pfi_msme_warped_1305_on_subject = jph(pfo_tmp, 'warp_1305_on_' + sj + '.nii.gz')
    #     cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} ; '.format(
    #         pfi_msme_tp0_up,
    #         pfi_1305,
    #         pfi_affine_transformation_1305_on_subject,
    #         pfi_msme_warped_1305_on_subject)
    #     os.system(cmd)
    #     # -- Propagate roi mask:
    #     pfi_1305_roi_mask = jph(pfo_utils, '1305', '1305_T1_roi_mask.nii.gz')
    #     pfi_affine_transformation_1305_on_subject = jph(pfo_tmp, 'aff_1305_on_' + sj + '.txt')
    #     assert os.path.exists(pfi_1305_roi_mask)
    #     assert os.path.exists(pfi_affine_transformation_1305_on_subject)
    #     pfi_up_roi_mask = jph(pfo_mask, sj + '_MSME_up_roi_mask.nii.gz')
    #     cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
    #         pfi_msme_tp0_up,
    #         pfi_1305_roi_mask,
    #         pfi_affine_transformation_1305_on_subject,
    #         pfi_up_roi_mask)
    #     os.system(cmd)
    #     # -- down_sampled roi mask
    #     pfi_msme_roi_mask = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
    #     cmd0 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(pfi_msme_tp0,
    #                                                                        pfi_up_roi_mask,
    #                                                                        pfi_affine_identity,
    #                                                                        pfi_msme_roi_mask)
    #     os.system(cmd0)

    if controller['register tp0 to S0']:
        print('- Processing MSME: register tp0 to S0 {}'.format(sj))
        pfi_s0 = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_s0_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_msme_tp0 = jph(pfo_output_sj, 'mod', sj + '_MSME_tp0.nii.gz')
        assert os.path.exists(pfi_s0)
        assert os.path.exists(pfi_s0_mask)
        assert os.path.exists(pfi_msme_tp0)
        pfi_transf_msme_on_s0 = jph(pfo_tmp, sj + '_msme_on_b0_rigid.txt')
        pfi_warped_msme_on_s0 = jph(pfo_mod, sj + '_MSME_tp0_up.nii.gz')
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -aff {3} -res {4} -rigOnly'.format(
            pfi_s0, pfi_s0_mask, pfi_msme_tp0, pfi_transf_msme_on_s0, pfi_warped_msme_on_s0
        )
        os.system(cmd)

    if controller['register msme to S0']:
        pfi_s0 = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_msme = jph(pfo_mod, sj + '_MSME.nii.gz')
        pfi_transf_msme_on_s0 = jph(pfo_tmp, sj + '_msme_on_b0_rigid.txt')
        assert os.path.exists(pfi_s0)
        assert os.path.exists(pfi_msme)
        assert os.path.exists(pfi_transf_msme_on_s0)
        pfi_msme_upsampled = jph(pfo_mod, sj + '_MSME_up.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 1'.format(
            pfi_s0, pfi_msme, pfi_transf_msme_on_s0, pfi_msme_upsampled
        )
        os.system(cmd)

    if controller['extract first tp in s0 space']:
        print('- Processing MSME: extract first layers {}'.format(sj))
        pfi_msme_upsampled = jph(pfo_mod, sj + '_MSME_up.nii.gz')
        assert os.path.exists(pfi_msme_upsampled)
        pfi_msme_updampled_first_layer = jph(pfo_output_sj, 'mod', sj + '_MSME_tp0_up.nii.gz')
        cmd0 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_upsampled, pfi_msme_updampled_first_layer)
        os.system(cmd0)


def process_MSME_from_list(subj_list, controller):

    print '\n\n Processing MSME subjects from list {} \n'.format(subj_list)
    for sj in subj_list:
        
        process_MSME_per_subject(sj, controller)


if __name__ == '__main__':
    print('process MSME, local run. ')

    controller_MSME = {'squeeze'                       : True,
                       'orient to standard'            : True,
                       'extract first timepoint'       : True,
                       'register tp0 to S0'            : True,
                       'register msme to S0'           : True,
                       'extract first tp in s0 space'  : True
                       }
    #
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    process_MSME_from_list(lsm.ls, controller_MSME)
