"""
You just received an new subject that was saved on Emporium.
You want to copy it to the cluster to have a second copy.
---
This is what you need! This module updates the cluster with new subjects (with extra care).
"""
import os
from os.path import join as jph
import pickle

from tools.definitions import root_main_emporium, pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager


def update_cluster_for_subject(sj):

    # input:
    pfi_param     = jph(pfo_subjects_parameters, sj)
    sj_parameters = pickle.load(open(pfi_param, 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    root_zipped_data_emporium = jph(root_main_emporium, 'rabbit', '00_raw_data_zipped')
    pfi_zipped_input  = jph(root_zipped_data_emporium, study, category, '{}.zip'.format(sj))

    assert os.path.exists(pfi_zipped_input), 'zipped file {} not found!'.format(pfi_zipped_input)

    # output:
    cluster_entry = 'ferraris@comic100.cs.ucl.ac.uk'
    root_data_cluster = '/cluster/project0/fetalsurgery/Data/MRI/KUL_preterm_rabbit_model/data/'
    pfo_where_to_copy_the_folder = jph(root_data_cluster, '00_raw_data_zipped', study, category) + '/'

    print('\n\nCommand:')
    cmd = 'scp -r {0} {1}:{2}'.format(pfi_zipped_input, cluster_entry, pfo_where_to_copy_the_folder)
    print(cmd)
    a = raw_input('Wait! Are you sure this is what you want??? (y/n) ...Think carefully...!!')

    if a == 'yes' or a == 'y':
        os.system(cmd)
        print('Subject {} copied\n\n'.format(sj))
    else:
        print('Subject {} NOT copied\n\n'.format(sj))


def update_cluster_for_subject_list(sj_list):
    print('UPDATE cluster with subject list {} \n'.format(sj_list))
    for sj in sj_list:
        print('\n-> Subject {}'.format(sj))
        update_cluster_for_subject(sj)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo01 = False
    lsm.execute_ACS_ex_vivo02 = False

    lsm.input_subjects = ['13003', '13403retest']

    lsm.update_ls()

    update_cluster_for_subject_list(lsm.ls)
