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
import pickle

from tools import definitions as defs
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from main_pipeline.U_utils import brain_tissue_multi_atlas_manager as btm


def get_brain_mask_per_subject(sj, sj_parameters):
    """
    From subject id, retrieves the subject parameters and creates its brain mask based upon them.
    :param sj: subject id.
    :param sj_parameters: subject parameters filtered from caller function.
    :return: brain of subject sj.
    """
    print('\nGet brain mask per subject {} started.\n'.format(sj))

    study    = sj_parameters['study']
    category = sj_parameters['category']

    options_brain_mask = sj_parameters['options_brain_mask']

    # Target folder in stereotaxic coordinates:
    pfo_sj = jph(defs.root_study_rabbits, 'A_data', study, category, sj)
    pfo_sc_sj = jph(pfo_sj, 'stereotaxic')

    pfo_tmp = jph(pfo_sc_sj, 'z_tmp_generate_brain_mask')
    cmd = 'mkdir -p {}'.format(pfo_tmp)
    print_and_run(cmd)

    # FINAL Output
    pfi_brain_mask_sj = jph(pfo_sc_sj, 'masks', '{}_brain_mask.nii.gz'.format(sj))

    # IF subject is in multi-atlas just copy the brain_mask to the new destination.
    if sj in defs.multi_atlas_subjects:
        # Input
        pfi_brain_mask_sj_atlas = jph(defs.root_atlas, sj, 'masks', '{}_brain_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_brain_mask_sj_atlas), pfi_brain_mask_sj_atlas
        # Command
        cmd = 'cp {} {}'.format(pfi_brain_mask_sj_atlas, pfi_brain_mask_sj)
        print_and_run(cmd)
    elif sj in defs.multi_atlas_BT_subjects:
        # Input
        pfi_brain_mask_sj_atlas = jph(defs.root_atlas_BT, '{}_brain_mask.nii.gz'.format(sj))
        assert os.path.exists(pfi_brain_mask_sj_atlas), pfi_brain_mask_sj_atlas
        # Command
        cmd = 'cp {} {}'.format(pfi_brain_mask_sj_atlas, pfi_brain_mask_sj)
        print_and_run(cmd)

    # ELSE: get the list of subjects of the atlas
    else:
        if options_brain_mask['method'] == 'MA':
            mutli_atlas_subject_list = defs.multi_atlas_subjects
        elif options_brain_mask['method'] == 'BTMA':
            mutli_atlas_subject_list = defs.multi_atlas_BT_subjects
        elif options_brain_mask['method'] == 'BTMA_MA' or options_brain_mask['method'] == 'MA_BTMA':
            mutli_atlas_subject_list = defs.multi_atlas_BT_subjects + defs.multi_atlas_subjects
        else:
            raise IOError('option for brain mask not existent.')

        print('\nMulti atlas for brain mask selected is {} .\n'.format(mutli_atlas_subject_list))

        # THEN: get the output brain mask from extenal function
        btm.extract_brain_tissue_from_multi_atlas_list_stereotaxic(sj, mutli_atlas_subject_list, pfo_tmp,
                                                                   pfi_output_brain_mask=pfi_brain_mask_sj,
                                                                   options=options_brain_mask)

    # Print end-of-procedure message:
    print('\nBrain mask per subject {} saved in {}.\n'.format(sj, pfi_brain_mask_sj))


def get_brain_mask_from_list(subj_list):

    print('\nGet brain mask per list {} started.\n'.format(subj_list))

    for sj in subj_list:

        sj_parameters = pickle.load(open(jph(defs.pfo_subjects_parameters, sj), 'r'))
        if sj_parameters['options_brain_mask']['method'] is None:
            print('=> No brain_mask required for subject {}. \n\n'.format(sj))
        else:
            get_brain_mask_per_subject(sj, sj_parameters)


if __name__ == '__main__':
    print('Get brain mask, local run.')

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    lsm.input_subjects = ['13102', '13201', '13202', '13401', '13402', '13403']
    lsm.update_ls()

    print lsm.ls

    get_brain_mask_from_list(lsm.ls)
