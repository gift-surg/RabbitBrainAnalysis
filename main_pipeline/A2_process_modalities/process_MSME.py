"""
MSME processing in their original coordinate system
"""
import os
from os.path import join as jph
import nibabel as nib
import pickle

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor, \
    percentile_lesion_mask_extractor_only_from_image_path
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero
from tools.auxiliary.squeezer import squeeze_image_from_path
from LABelsToolkit.tools.aux_methods.utils import print_and_run
from LABelsToolkit.tools.aux_methods.sanity_checks import check_path_validity
from tools.correctors.bias_field_corrector4 import bias_field_correction

"""

Processing list for each MSME of each subject:

output that we want is in mod folder for each subject:
> original, no corrections -> <id>_MSME.nii.gz
> original BFC             -> <id>_MSME_BFC.nii.gz
> upsampled to S0          -> <id>_MSMEinS0.nii.gz
> upsampled to S0 BFC      -> <id>_MSMEinS0_BFC.nii.gz

> upsampled to S0          -> <id>_MSMEinS0.nii.gz
> upsampled to S0 BFC      -> <id>_MSMEinS0_BFC.nii.gz

in mod folder, a z_MSME with the first timepoints. Same as before, ending with _tp0.nii.gz .

Generate intermediate folder
Generate output folder
squeeze
Orient to standard - fsl

squeeze
orient to standard
extract first timepoint
Upsample MSMEtp0 to the grid spacing of S0 (id affine transformation).
-> Outcome MSMEup will be an extra modality for the segmentation propagation in its own space.
bfc
Save the bias field corrected in original space and the MSMEup as extra modality for the
segmentatino propagation.

"""


def process_MSME_per_subject(sj, controller):
    print('\nProcessing MSME, subject {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    if sj not in list_all_subjects(pfo_subjects_parameters):
        raise IOError('Subject parameters not known')

    study    = sj_parameters['study']
    category = sj_parameters['category']

    pfo_input_sj  = jph(root_study_rabbits, '02_nifti', study, category, sj)
    pfo_output_sj = jph(root_study_rabbits, 'A_data', study, category, sj)


    if not os.path.exists(pfo_input_sj):
        raise IOError('Input folder Subject does not exist.')

    # -- Generate intermediate and output folders:

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'masks')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_MSME')

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    if controller['squeeze']:
        print('- Processing MSME: squeeze {}'.format(sj))
        pfi_msme_nifti = jph(pfo_input_sj, sj + '_MSME', sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme_nifti)
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        squeeze_image_from_path(pfi_msme_nifti, pfi_msme, copy_anyway=True)

    if controller['orient_to_standard']:
        print('- Processing MSME: orient to standard {}'.format(sj))
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        assert check_path_validity(pfi_msme)
        cmd = 'fslreorient2std {0} {0}'.format(pfi_msme)
        print_and_run(cmd)
        set_translational_part_to_zero(pfi_msme, pfi_msme)

    if controller['extract_first_timepoint']:
        print('- Processing MSME: extract first layers {}'.format(sj))
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        pfi_msme_original_first_layer = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')
        cmd0 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme, pfi_msme_original_first_layer)
        print_and_run(cmd0)

    if controller['register_tp0_to_S0']:

        print('- Processing MSME: create ficticious original MSME mask {}'.format(sj))
        pfi_msme_original_first_layer = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')

        print('- Processing MSME: register tp0 to S0 {}'.format(sj))
        pfi_s0 = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_s0_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        pfi_msme_tp0 = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')
        assert os.path.exists(pfi_s0)
        assert os.path.exists(pfi_s0_mask)
        assert check_path_validity(pfi_msme_tp0)
        pfi_transf_msme_on_s0 = jph(pfo_tmp, sj + '_msme_on_S0_rigid.txt')
        pfi_warped_msme_on_s0 = jph(pfo_tmp, sj + '_MSME_tp0_up.nii.gz')
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -aff {3} -res {4} -omp {5} -rigOnly'.format(
            pfi_s0, pfi_s0_mask, pfi_msme_tp0, pfi_transf_msme_on_s0, pfi_warped_msme_on_s0, num_cores_run
        )
        print_and_run(cmd)

    if controller['register_msme_to_S0']:
        pfi_s0 = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        pfi_transf_msme_on_s0 = jph(pfo_tmp, sj + '_msme_on_S0_rigid.txt')
        assert os.path.exists(pfi_s0)
        assert os.path.exists(pfi_msme)
        assert check_path_validity(pfi_transf_msme_on_s0)
        pfi_msme_upsampled = jph(pfo_tmp, sj + '_MSMEinS0.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 1'.format(
            pfi_s0, pfi_msme, pfi_transf_msme_on_s0, pfi_msme_upsampled
        )
        print_and_run(cmd)

    if controller['get_mask_for_original_msme']:
        print('- Processing MSME: get mask for original msme:')
        # Start from the S0 mask (this will be saved as an extra mask as MSMEinS0 mask).
        pfi_s0_mask = jph(pfo_mask, '{}_S0_roi_mask.nii.gz'.format(sj))
        pfi_warped_msme_on_s0 = jph(pfo_tmp, sj + '_MSME_tp0_up.nii.gz')
        assert os.path.exists(pfi_s0_mask), pfi_s0_mask
        assert os.path.exists(pfi_warped_msme_on_s0), pfi_warped_msme_on_s0
        pfi_msme_up_lesion_mask = jph(pfo_tmp, '{}_msme_up_lesions_mask.nii.gz'.format(sj))
        pfi_msme_up_reg_mask = jph(pfo_tmp, '{}_msme_up_reg_mask.nii.gz'.format(sj))
        # Crop it properly to the MSMEinS0.
        percentile_lesion_mask_extractor(im_input_path=pfi_warped_msme_on_s0,
                                         im_output_path=pfi_msme_up_lesion_mask,
                                         im_mask_foreground_path=pfi_s0_mask,
                                         percentiles=(10, 98),
                                         safety_on=False)
        cmd = 'seg_maths {0} -sub {1} {2}'.format(pfi_s0_mask, pfi_msme_up_lesion_mask, pfi_msme_up_reg_mask)
        print_and_run(cmd)
        # Register MSMEinS0 with an approximative new mask over the original with no mask.
        pfi_msme_original_first_layer = jph(pfo_tmp, '{}_MSME_tp0.nii.gz'.format(sj))
        pfi_msme_original_pre_mask = jph(pfo_tmp, '{}_MSME_tp0_pre_mask.nii.gz'.format(sj))
        percentile_lesion_mask_extractor_only_from_image_path(pfi_msme_original_first_layer,
                                                              pfi_msme_original_pre_mask,
                                                              percentile_range=(30, 95))  # TODO, personal attribute?

        pfi_warped_msme_on_s0_back_on_msme = jph(pfo_tmp, '{}_warped_msme_on_s0_back_on_msme.nii.gz'.format(sj))
        pfi_affine_msme_on_s0_back_on_msme = jph(pfo_tmp, '{}_affine_msme_on_s0_back_on_msme.txt'.format(sj))
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -res {4} -aff {5} -omp {6} -rigOnly'.format(
            pfi_msme_original_first_layer, pfi_msme_original_pre_mask, pfi_warped_msme_on_s0, pfi_s0_mask,
            pfi_warped_msme_on_s0_back_on_msme, pfi_affine_msme_on_s0_back_on_msme, num_cores_run
        )
        print_and_run(cmd)
        # Apply transformation to the S0 roi_mask and to S0 reg_mask

        for ma in ['roi_mask', 'reg_mask']:
            S0_mask = jph(pfo_mask, '{0}_S0_{1}.nii.gz'.format(sj, ma))
            assert os.path.exists(S0_mask)
            MSME_mask = jph(pfo_mask, '{0}_MSME_{1}.nii.gz'.format(sj, ma))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_msme_original_first_layer, S0_mask, pfi_affine_msme_on_s0_back_on_msme, MSME_mask
            )
            print_and_run(cmd)

        # print('back-propagate the S0 mask on the MSME:')
        # pfi_aff = jph(pfo_tmp, sj + '_msme_on_S0_rigid.txt')
        # assert os.path.exists(pfi_aff)
        # # this very same transformation must be used to back propagate the segmentations!
        # pfi_inv_aff = jph(pfo_tmp, sj + '_S0_on_msmse_rigid.txt')
        # cmd0 = 'reg_transform -invAff {0} {1}'.format(pfi_aff, pfi_inv_aff)
        # print_and_run(cmd0)
        # pfi_S0_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        # pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        # assert os.path.exists(pfi_S0_mask)
        # assert os.path.exists(pfi_msme)
        # pfi_mask_on_msme = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
        # cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
        #     pfi_msme, pfi_S0_mask, pfi_inv_aff, pfi_mask_on_msme)
        # print_and_run(cmd1)
        # print('Dilate:')
        # assert check_path_validity(pfi_mask_on_msme)
        # dil_factor = 0
        # cmd0 = 'seg_maths {0} -dil {1} {2}'.format(pfi_mask_on_msme, dil_factor, pfi_mask_on_msme)
        # print_and_run(cmd0)

    if controller['bfc']:
        print('- get bfc correction each slice:')
        pfi_msme_original = jph(pfo_tmp, sj + '_MSME.nii.gz')
        assert check_path_validity(pfi_msme_original)
        print('-- un-pack slices')
        im = nib.load(pfi_msme_original)
        tps = im.shape[-1]
        for tp in range(tps):
            pfi_tp = jph(pfo_tmp, sj + '_MSME_tp{}.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -tp {1} {2}'.format(pfi_msme_original, tp, pfi_tp)
            print_and_run(cmd0)
        print('-- bias-field correct the first slice')
        # bfc_param = subject[sj][3]
        bfc_param = [0.001, (50, 50, 50, 50), 0.15, 0.01, 400, (4, 4, 4), 3]
        pfi_tp0 = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')
        pfi_tp0_bfc = jph(pfo_tmp, sj + '_MSME_tp0_bfc.nii.gz')
        pfi_mask_on_msme = jph(pfo_mask, sj + '_MSME_roi_mask.nii.gz')
        assert os.path.exists(pfi_mask_on_msme)
        bias_field_correction(pfi_tp0, pfi_tp0_bfc,
                              pfi_mask=pfi_mask_on_msme,
                              prefix='',
                              convergenceThreshold=bfc_param[0],
                              maximumNumberOfIterations=bfc_param[1],
                              biasFieldFullWidthAtHalfMaximum=bfc_param[2],
                              wienerFilterNoise=bfc_param[3],
                              numberOfHistogramBins=bfc_param[4],
                              numberOfControlPoints=bfc_param[5],
                              splineOrder=bfc_param[6],
                              print_only=False)
        print('-- get the bias field from the bfc corrected')
        bias_field = jph(pfo_tmp, sj + '_bfc.nii.gz')
        cmd0 = 'seg_maths {0} -div {1} {2}'.format(pfi_tp0_bfc, pfi_tp0, bias_field)
        cmd1 = 'seg_maths {0} -removenan {0}'.format(bias_field)
        print_and_run(cmd0)
        print_and_run(cmd1)
        assert check_path_validity(bias_field)
        print('-- correct all the remaining slices')
        for tp in range(1, tps):
            pfi_tp = jph(pfo_tmp, sj + '_MSME_tp{}.nii.gz'.format(tp))
            pfi_tp_bfc = jph(pfo_tmp, sj + '_MSME_tp{}_bfc.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -mul {1} {2}'.format(pfi_tp, bias_field, pfi_tp_bfc)
            print_and_run(cmd0)
            check_path_validity(pfi_tp_bfc)
        print('-- pack together all the images in a stack')
        cmd = 'seg_maths {0} -merge	{1} {2} '.format(pfi_tp0_bfc, tps-1, 4)
        for tp in range(1, tps):
            pfi_tp_bfc = jph(pfo_tmp, sj + '_MSME_tp{}_bfc.nii.gz'.format(tp))
            cmd += pfi_tp_bfc + ' '
        pfi_stack = jph(pfo_tmp, sj + '_MSME_BFC.nii.gz')
        cmd += pfi_stack

        print_and_run(cmd)

    if controller['bfc_up']:
        print('- get bfc correction each slice:')
        pfi_msme_upsampled = jph(pfo_tmp, sj + '_MSMEinS0.nii.gz')
        assert check_path_validity(pfi_msme_upsampled)
        print('-- un-pack slices')
        im = nib.load(pfi_msme_upsampled)
        tps = im.shape[-1]
        for tp in range(tps):
            pfi_up_tp = jph(pfo_tmp, sj + '_MSMEinS0_tp{}.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -tp {1} {2}'.format(pfi_msme_upsampled, tp, pfi_up_tp)
            print_and_run(cmd0)
        print('-- bias-field correct the first slice')
        # bfc_param = subject[sj][3]
        bfc_param = [0.001, (50, 50, 50, 50), 0.15, 0.01, 400, (4, 4, 4), 3]
        pfi_up_tp0 = jph(pfo_tmp, sj + '_MSMEinS0_tp0.nii.gz')
        pfi_up_tp0_bfc = jph(pfo_tmp, sj + '_MSMEinS0_tp0_BFC.nii.gz')
        pfi_mask = jph(pfo_mask, sj + '_S0_roi_mask.nii.gz')
        bias_field_correction(pfi_up_tp0, pfi_up_tp0_bfc,
                              pfi_mask=pfi_mask,
                              prefix='',
                              convergenceThreshold=bfc_param[0],
                              maximumNumberOfIterations=bfc_param[1],
                              biasFieldFullWidthAtHalfMaximum=bfc_param[2],
                              wienerFilterNoise=bfc_param[3],
                              numberOfHistogramBins=bfc_param[4],
                              numberOfControlPoints=bfc_param[5],
                              splineOrder=bfc_param[6],
                              print_only=False)
        print('-- get the bias field from the bfc corrected')
        bias_field_up = jph(pfo_tmp, sj + '_bfc_up.nii.gz')
        cmd0 = 'seg_maths {0} -div {1} {2}'.format(pfi_up_tp0_bfc, pfi_up_tp0, bias_field_up)
        cmd1 = 'seg_maths {0} -removenan {0}'.format(bias_field_up)
        print_and_run(cmd0)
        print_and_run(cmd1)
        assert check_path_validity(bias_field_up)
        print('-- correct all the remaining slices')
        for tp in range(1, tps):
            pfi_up_tp = jph(pfo_tmp, sj + '_MSMEinS0_tp{}.nii.gz'.format(tp))
            pfi_up_tp_bfc = jph(pfo_tmp, sj + '_MSMEinS0_tp{}_bfc.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -mul {1} {2}'.format(pfi_up_tp, bias_field_up, pfi_up_tp_bfc)
            print_and_run(cmd0)
            check_path_validity(pfi_up_tp_bfc)
        print('-- pack together all the images in a stack')
        cmd_merge = 'seg_maths {0} -merge	{1} {2} '.format(pfi_up_tp0_bfc, tps-1, 4)
        for tp in range(1, tps):
            pfi_up_tp_bfc = jph(pfo_tmp, sj + '_MSMEinS0_tp{}_bfc.nii.gz'.format(tp))
            cmd_merge += pfi_up_tp_bfc + ' '
        pfi_stack_up = jph(pfo_tmp, sj + '_MSMEinS0_BFC.nii.gz')
        cmd_merge += pfi_stack_up

        print_and_run(cmd_merge)

    if controller['save_results']:
        print('save results -  save only the bias field corrected as they proved to have the same results.')
        pfi_msme_nifti  = jph(pfo_tmp, sj + '_MSME.nii.gz')  # original
        pfi_msme_bfc    = jph(pfo_tmp, sj + '_MSME_BFC.nii.gz')  # original bfc
        pfi_msme_up     = jph(pfo_tmp, sj + '_MSMEinS0.nii.gz')  # up
        pfi_msme_up_bfc = jph(pfo_tmp, sj + '_MSMEinS0_BFC.nii.gz')  # up bfc
        assert check_path_validity(pfi_msme_nifti)
        assert check_path_validity(pfi_msme_bfc)
        assert check_path_validity(pfi_msme_up)
        assert check_path_validity(pfi_msme_up_bfc)
        # pfi_final        = jph(pfo_mod, sj + '_MSME.nii.gz')
        pfi_final_bfc    = jph(pfo_mod, sj + '_MSME.nii.gz')
        # pfi_final_up     = jph(pfo_mod, sj + '_MSMEinS0.nii.gz')
        pfi_final_bfc_up = jph(pfo_mod, sj + '_MSMEinS0.nii.gz')
        # cmd0 = 'cp {0} {1}'.format(pfi_msme_nifti, pfi_final)
        # cmd2 = 'cp {0} {1}'.format(pfi_msme_up, pfi_final_up)
        cmd1 = 'cp {0} {1}'.format(pfi_msme_bfc, pfi_final_bfc)
        cmd3 = 'cp {0} {1}'.format(pfi_msme_up_bfc, pfi_final_bfc_up)
        # print_and_run(cmd0)
        # print_and_run(cmd2)
        print_and_run(cmd1)
        print_and_run(cmd3)

    if controller['save_results_tp0']:
        print('save results - timepoint zero, only the bfc')
        # pfi_msme_nifti  = jph(pfo_tmp, sj + '_MSME.nii.gz')  # original
        # pfi_msme_up     = jph(pfo_tmp, sj + '_MSMEinS0.nii.gz')  # up
        pfi_msme_bfc    = jph(pfo_tmp, sj + '_MSME_BFC.nii.gz')  # original bfc
        pfi_msme_up_bfc = jph(pfo_tmp, sj + '_MSMEinS0_BFC.nii.gz')  # up bfc
        # assert check_path_validity(pfi_msme_nifti)
        # assert check_path_validity(pfi_msme_up)
        assert check_path_validity(pfi_msme_bfc)
        assert check_path_validity(pfi_msme_up_bfc)
        pfo_tp0 = jph(pfo_mod, 'MSME_tp0')
        # pfi_final_tp0        = jph(pfo_tp0, sj + '_MSME_tp0.nii.gz')
        # pfi_final_up_tp0     = jph(pfo_tp0, sj + '_MSMEinS0_tp0.nii.gz')
        pfi_final_bfc_tp0    = jph(pfo_tp0, sj + '_MSME_tp0.nii.gz')
        pfi_final_bfc_up_tp0 = jph(pfo_tp0, sj + '_MSMEinS0_tp0.nii.gz')
        cmd0 = 'mkdir -p {}'.format(pfo_tp0)
        # cmd1 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_nifti, pfi_final_tp0)
        # cmd3 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_up, pfi_final_up_tp0)
        cmd2 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_bfc, pfi_final_bfc_tp0)

        cmd4 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme_up_bfc, pfi_final_bfc_up_tp0)
        print_and_run(cmd0)
        # print_and_run(cmd1)
        # print_and_run(cmd3)
        print_and_run(cmd2)
        print_and_run(cmd4)


def process_MSME_from_list(subj_list, controller):

    print '\n\n Processing MSME subjects from list {} \n'.format(subj_list)
    for sj in subj_list:
        
        process_MSME_per_subject(sj, controller)


if __name__ == '__main__':
    print('process MSME, local run. ')

    controller_MSME = {'squeeze'                       : True,
                       'orient_to_standard'            : True,
                       'extract_first_timepoint'       : True,
                       'register_tp0_to_S0'            : True,
                       'register_msme_to_S0'           : True,
                       'get_mask_for_original_msme'    : True,
                       'bfc'                           : False,
                       'bfc_up'                        : False,
                       'save_results'                  : False,
                       'save_results_tp0'              : False
                       }
    #
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['1201']  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    process_MSME_from_list(lsm.ls, controller_MSME)
