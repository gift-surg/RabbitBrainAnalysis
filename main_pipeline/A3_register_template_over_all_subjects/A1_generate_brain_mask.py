"""
SPOT a Neonatal Rabbit has some options for more accurate segmentation propagation
requiring a mask of the brain tissue. This module is aimed at providing this
mask, using again a segmentation propagation approach.
---
This module works only with data in stereotaxic coordinates. The target is already in stereotaxic and so
 they are the multi-atlas that are supporting the brain tissue segmentation.
"""
import os
from os.path import join as jph
import numpy as np
import pickle

from tools.definitions import root_atlas_BT, pfo_subjects_parameters, multi_atlas_brain_tissue_subjects, \
    root_study_rabbits, num_cores_run, multi_atlas_subjects, root_atlas
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from main_pipeline.U_utils.brain_tissue_multi_atlas_manager import extract_brain_tissue_from_multi_atlas


def get_brain_mask_per_subject(sj):
    """
    From subject id, retrieves the subject parameters and creates its brain mask based upon them.
    :param sj: subject id.
    :return: brain of subject sj.
    """
    print('\nGet brain mask per subject {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study    = sj_parameters['study']
    category = sj_parameters['category']

    options_brain_mask = sj_parameters['options_brain_mask']

    # Target folder in stereotaxic coordinates:
    pfo_sj = jph(root_study_rabbits, 'A_data', study, category, sj)
    pfo_sc_sj = jph(pfo_sj, 'stereotaxic')
    pfo_sc_sj_mod = jph(pfo_sc_sj, 'mod')
    pfo_sc_sj_masks = jph(pfo_sc_sj, 'masks')

    pfo_tmp = jph(pfo_sc_sj, 'z_tmp_generate_brain_mask')


    if sj_parameters['in_atlas']:
        # if subject is in multi-atlas just
        pfi_roi_mask = jph(pfo_sc_sj_masks, '{}_T1_roi_mask.nii.gz'.format(sj))
        pfi_reg_mask = jph(pfo_sc_sj_masks, '{}_T1_reg_mask.nii.gz'.format(sj))

        cmd = 'cp {} {}'.format(pfi_roi_mask_not_adjusted, pfi_roi_mask)
        print_and_run(cmd)
        cmd = 'cp {} {}'.format(pfi_reg_mask_not_adjusted, pfi_reg_mask)
        print_and_run(cmd)
    else:

        if options_brain_mask['modality'] == 'MA':
            mutli_atlas_subject_list = multi_atlas_subjects
        elif options_brain_mask['modality'] == 'BTMA':
            mutli_atlas_subject_list = multi_atlas_brain_tissue_subjects
        elif options_brain_mask['modality'] == 'BTMA_MA' or options_brain_mask['modality'] == 'MA_BTMA':
            mutli_atlas_subject_list = multi_atlas_brain_tissue_subjects + multi_atlas_subjects
        else:
            raise IOError





    # Selecting the roi mask extraction modality if not in atlas
    if options_brain_mask['roi_mask'] == 'BTMA' or options_brain_mask['roi_mask'] == 'MA' and not sj_parameters['in_atlas']:

        # Robust roi extraction - uses the binarised brain tissue for the partial skull stripping.
        # This should be modified to get the slim registration, otherwise is an overkill
        print('- Get roi masks from each subject of the multi-atlas {} on {}'.format(options_brain_mask['roi_mask'], sj))

        pfi_target_T1 = jph(pfo_tmp, '{}_to_std.nii.gz'.format(sj))
        pfi_roi_mask_not_adjusted = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted.nii.gz')

        assert os.path.exists(pfi_target_T1), pfi_target_T1
        assert os.path.exists(pfi_roi_mask_not_adjusted), pfi_roi_mask_not_adjusted

        pfi_output_brain_mask = jph(pfo_mask, '{}_T1_brain_mask.nii.gz'.format(sj))

        alpha = 0
        if options_T1['roi_mask'] == 'MA':
            alpha = np.pi / 8

        extract_brain_tissue_from_multi_atlas(target_name=sj,
                                              pfi_target_T1=pfi_target_T1,
                                              pfi_output_brain_mask=pfi_output_brain_mask,
                                              pfi_target_pre_mask=pfi_roi_mask_not_adjusted,
                                              pfo_tmp=pfo_tmp, alpha=alpha)

    if options_brain_mask['modality'] == 'BTMA' or options_brain_mask['modality'] == 'MA':
        # -> we have a brain mask
        pfi_output_brain_mask = jph(pfo_mask, '{}_T1_brain_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_output_brain_mask), pfi_output_brain_mask

        dilation_param = options_T1['mask_dilation']
        if dilation_param < 0:  # if negative, erode.
            cmd = 'seg_maths {0} -ero {1} {2}'.format(pfi_output_brain_mask,
                                                      -1 * dilation_param,
                                                      pfi_roi_mask)
        elif dilation_param > 0:
            cmd = 'seg_maths {0} -dil {1} {2}'.format(pfi_output_brain_mask,
                                                      dilation_param,
                                                      pfi_roi_mask)
        else:
            cmd = 'cp {} {}'.format(pfi_output_brain_mask, pfi_roi_mask)

        del pfi_output_brain_mask, dilation_param
    else:
        pass


def get_brain_mask_per_subject_from_list(subj_list):

    print('\nGet brain mask per list {} started.\n'.format(subj_list))
    for sj in subj_list:

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        if sj_parameters['options_brain_mask']['method'] is None:
            print('No brain_mask required for subject {}'.format(sj))
        else:
            get_brain_mask_per_subject(sj)


if __name__ == '__main__':
    print('Get brain mask, local run.')

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['13102', ]
    lsm.update_ls()

    print lsm.ls

    get_brain_mask_per_subject_from_list(lsm.ls)
