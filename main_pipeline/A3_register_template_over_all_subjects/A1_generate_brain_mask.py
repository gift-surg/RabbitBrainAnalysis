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

from tools.definitions import root_atlas_BT, pfo_subjects_parameters, multi_atlas_BT_subjects, \
    root_study_rabbits, num_cores_run, multi_atlas_subjects, root_atlas
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from main_pipeline.U_utils.brain_tissue_multi_atlas_manager import extract_brain_tissue_from_multi_atlas, extract_brain_tissue_from_multi_atlas_list_stereotaxic


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
    cmd = 'mkdir -p {}'.format(pfo_tmp)
    print_and_run(cmd)

    # FINAL Output
    pfi_brain_mask_sj = jph(pfo_sc_sj_masks, '{}_brain_mask.nii.gz'.format(sj))

    # IF subject is in multi-atlas just copy the brain_mask to the new destination.
    if sj in multi_atlas_subjects:
        # Input
        pfi_brain_mask_sj_atlas = jph(root_atlas, sj, 'masks', '{}_brain_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_brain_mask_sj_atlas), pfi_brain_mask_sj_atlas
        # Command
        cmd = 'cp {} {}'.format(pfi_brain_mask_sj_atlas, pfi_brain_mask_sj)
        print_and_run(cmd)
    elif sj in multi_atlas_BT_subjects:
        # Input
        pfi_brain_mask_sj_atlas = jph(root_atlas_BT, '{}_brain_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_brain_mask_sj_atlas), pfi_brain_mask_sj_atlas
        # Command
        cmd = 'cp {} {}'.format(pfi_brain_mask_sj_atlas, pfi_brain_mask_sj)
        print_and_run(cmd)

    # ELSE: get the list of subjects of the atlas
    else:
        if options_brain_mask['modality'] == 'MA':
            mutli_atlas_subject_list = multi_atlas_subjects
        elif options_brain_mask['modality'] == 'BTMA':
            mutli_atlas_subject_list = multi_atlas_BT_subjects
        elif options_brain_mask['modality'] == 'BTMA_MA' or options_brain_mask['modality'] == 'MA_BTMA':
            mutli_atlas_subject_list = multi_atlas_BT_subjects + multi_atlas_subjects
        else:
            raise IOError

        # THEN: get the output
        extract_brain_tissue_from_multi_atlas_list_stereotaxic(sj, mutli_atlas_subject_list, pfo_tmp,
                                                               pfi_output=pfi_brain_mask_sj,
                                                               options=options_brain_mask)

    # Get finish message
    print('\nBrain mask per subject {} saved in {}.\n'.format(sj, pfi_brain_mask_sj))


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
