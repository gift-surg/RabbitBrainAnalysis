import os
from os.path import join as jph
import pickle

from nilabels.tools.aux_methods.utils import print_and_run

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits, pfo_subjects_parameters


def zip_a_subject_and_send(sj, pfo_sharing):

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study    = sj_parameters['study']
    category = sj_parameters['category']

    # zip the subject with no intermediate files:
    root_subjects = jph(root_study_rabbits, 'A_data', study, category)
    unzipped_folder_name = sj
    zipped_folder_name = '{}.zip'.format(sj)
    cmd = 'pushd {0}; zip -r {1} {2} -x ".DS_store" -x "__MACOSX"  -x "*z_tmp*" -x "*z_SPOT*"  '.format(root_subjects, zipped_folder_name, unzipped_folder_name)
    print_and_run(cmd)

    # move the zipped in the shared folder.
    pfi_zipped = jph(root_subjects, zipped_folder_name)
    assert os.path.exists(pfi_zipped)
    where_to_move_zipped = jph(pfo_sharing, zipped_folder_name)
    cmd = 'mv {} {}'.format(pfi_zipped, where_to_move_zipped)
    print_and_run(cmd)


def zip_and_send_list(sj_list, pfo_sharing):
    print('Sharing subjects {} to folder {}'.format(sj_list, pfo_sharing))
    for sj in sj_list:
        print('You are sharing the subject {} with Hannes. '
              'This implies that the subject is well segmented and underwent Quality Control!'.format(sj))
        zip_a_subject_and_send(sj, pfo_sharing)


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    # preterm = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '2002',
    #            '3301', '3303', '3404', '4302', '4304', '4305', '4901',
    #            '4903', '5001']
    #
    # # '1501', '1504' '1508', '1509', '1511', '2013', '2202', '2205', '2206' : in vivo and not in subjects parameters.
    # # '4303','4406', :  not yet elaborated.
    #
    # term = ['2502', '2503', '2608', '4501', '4504', '4507', '4601', '4603', '13003', '13004',
    #         '13005', '13006']
    # # '2605', '2702', '4602',  not yet elaborated.
    #
    # lsm.input_subjects = preterm + term
    #
    lsm.input_subjects = ['13601', '13603', '13604', '13605', '13610', '13706', '13707']


    lsm.update_ls()

    print lsm.ls

    destination_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/Processed'
    assert os.path.exists(destination_folder)

    zip_and_send_list(lsm.ls, destination_folder)
