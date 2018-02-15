""" -------------------
C) From the segmented chart in stereotaxic coordinates, the segmentations are moved back to
the
------------------- """
import os
from os.path import join as jph
import pickle

from labels_manager.main import LabelsManager

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_atlas, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run
from tools.auxiliary.multichannel import stack_a_list_of_images_from_list_pfi


def propagate_segmentation_in_original_space_per_subject(sj, controller, options):

    print('\nfrom Stereotaxic orientation to original space - SUBJECT {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    # recover the source in stereotaxic coordinates:
    if sj_parameters['in_atlas']:
        # source in stereotaxic coordinate is in the atlas
        return

    else:
        pass



def propagate_segmentation_in_original_space_from_list(subj_list, controller, options):
    print '\n\n Move to stereotaxic coordinate from list {} \n'.format(subj_list)
    for sj in subj_list:
        propagate_segmentation_in_original_space_per_subject(sj, controller, options)

if __name__ == '__main__':
    print('Propagate from Stereotaxic orientation to original space, local run. ')

    controller_ = {
        'Register_T1': True,
        'Propagate_T1_masks': True,
        'Register_S0': True,
        'Propagate_S0_related_mods_and_mask': True,
        'Adjustments': True
    }

    options_ = {
        'Template_chart_path': jph(root_atlas, '1305'),
        'Template_name': '1305'}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['4302']
    lsm.update_ls()

    propagate_segmentation_in_original_space_per_subject(lsm.ls, controller_, options_)

