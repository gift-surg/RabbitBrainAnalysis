"""
MSME processing in their original coordinate system
"""
import os
from os.path import join as jph
import nibabel as nib
import numpy as np

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import set_new_data
from tools.correctors.bias_field_corrector4 import bias_field_correction
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
        pfi_msme_nifti = jph(pfo_input_sj, sj + '_MSME', sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme_nifti)
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        squeeze_image_from_path(pfi_msme_nifti, pfi_msme, copy_anyway=True)

    if controller['orient to standard']:
        print('- Processing MSME: orient to standard {}'.format(sj))
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        cmd = 'fslreorient2std {0} {0}'.format(pfi_msme)
        os.system(cmd)
        set_translational_part_to_zero(pfi_msme, pfi_msme)

    if controller['extract first timepoint']:
        print('- Processing MSME: extract first layers {}'.format(sj))
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        assert os.path.exists(pfi_msme)
        pfi_msme_original_first_layer = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')
        cmd0 = 'seg_maths {0} -tp 0 {1}'.format(pfi_msme, pfi_msme_original_first_layer)
        os.system(cmd0)

    if controller['register tp0 to S0']:
        print('- Processing MSME: register tp0 to S0 {}'.format(sj))
        pfi_s0 = jph(pfo_mod, sj + '_S0.nii.gz')
        pfi_s0_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_msme_tp0 = jph(pfo_tmp, sj + '_MSME_tp0.nii.gz')
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
        pfi_msme = jph(pfo_tmp, sj + '_MSME.nii.gz')
        pfi_transf_msme_on_s0 = jph(pfo_tmp, sj + '_msme_on_b0_rigid.txt')
        assert os.path.exists(pfi_s0)
        assert os.path.exists(pfi_msme)
        assert os.path.exists(pfi_transf_msme_on_s0)
        pfi_msme_upsampled = jph(pfo_tmp, sj + '_MSME_up.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 1'.format(
            pfi_s0, pfi_msme, pfi_transf_msme_on_s0, pfi_msme_upsampled
        )
        os.system(cmd)

    if controller['bfc']:
        print('- get bfc correction each slice:')
        pfi_msme_upsampled = jph(pfo_tmp, sj + '_MSME_up.nii.gz')
        assert os.path.exists(pfi_msme_upsampled)
        print('-- un-pack slices')
        im = nib.load(pfi_msme_upsampled)
        tps = im.shape[-1]
        for tp in range(tps):
            pfi_tp = jph(pfo_tmp, sj + '_MSME_tp{}.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -tp {1} {2}'.format(pfi_msme_upsampled, tp, pfi_tp)
            os.system(cmd0)
        print('-- bias-field correct the first slice')
        # bfc_param = subject[sj][3]
        bfc_param = [0.001, (50, 50, 50, 50), 0.15, 0.01, 400, (4, 4, 4), 3]
        pfi_tp0 = jph(pfo_tmp, sj + '_MSME_tp{}.nii.gz'.format(0))
        pfi_tp0_bfc = jph(pfo_tmp, sj + '_MSME_tp0_bfc.nii.gz')
        pfi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        bias_field_correction(pfi_tp0, pfi_tp0_bfc,
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
        bias_field = jph(pfo_tmp, sj + '_bfc.nii.gz')
        cmd0 = 'seg_maths {0} -div {1} {2}'.format(pfi_tp0_bfc, pfi_tp0, bias_field)
        cmd1 = 'seg_maths {0} -removenan {0}'.format(bias_field)
        os.system(cmd0)
        os.system(cmd1)
        print('-- correct all the remaining slices')
        for tp in range(1, tps):
            pfi_tp = jph(pfo_tmp, sj + '_MSME_tp{}.nii.gz'.format(tp))
            pfi_tp_bfc = jph(pfo_tmp, sj + '_MSME_tp{}_bfc.nii.gz'.format(tp))
            cmd0 = 'seg_maths {0} -mul {1} {2}'.format(pfi_tp, bias_field, pfi_tp_bfc)
            os.system(cmd0)
        print('-- pack together all the images in a stack')
        cmd = 'seg_maths {0} -merge	{1} {2} '.format(pfi_tp0_bfc, tps-1, 4)
        for tp in range(1, tps):
            pfi_tp_bfc = jph(pfo_tmp, sj + '_MSME_tp{}_bfc.nii.gz'.format(tp))
            print
            print pfi_tp_bfc
            print
            cmd += pfi_tp_bfc + ' '
        pfi_stack = jph(pfo_tmp, sj + '_MSME_up_bfc.nii.gz')
        cmd += pfi_stack

        print
        print cmd
        os.system(cmd)

    if controller['save results']:
        print('save results')
        pfi_stack = jph(pfo_tmp, sj + '_MSME_up_bfc.nii.gz')
        pfi_tp0_bfc = jph(pfo_tmp, sj + '_MSME_tp0_bfc.nii.gz')
        assert os.path.exists(pfi_stack)
        assert os.path.exists(pfi_tp0_bfc)
        pfi_msme_updampled_and_bfc = jph(pfo_mod, sj + '_MSME_up.nii.gz')
        pfi_msme_updampled_first_layer = jph(pfo_mod, sj + '_MSME_tp0_up.nii.gz')
        cmd2 = 'cp {0} {1}'.format(pfi_stack, pfi_msme_updampled_and_bfc)
        cmd3 = 'cp {0} {1}'.format(pfi_tp0_bfc, pfi_msme_updampled_first_layer)
        os.system(cmd2)
        os.system(cmd3)


def process_MSME_from_list(subj_list, controller):

    print '\n\n Processing MSME subjects from list {} \n'.format(subj_list)
    for sj in subj_list:
        
        process_MSME_per_subject(sj, controller)


if __name__ == '__main__':
    print('process MSME, local run. ')

    controller_MSME = {'squeeze'                       : False,
                       'orient to standard'            : False,
                       'extract first timepoint'       : False,
                       'register tp0 to S0'            : False,
                       'register msme to S0'           : False,
                       'bfc'                           : False,
                       'save results'                  : True
                       }
    #
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['3103', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    process_MSME_from_list(lsm.ls, controller_MSME)
