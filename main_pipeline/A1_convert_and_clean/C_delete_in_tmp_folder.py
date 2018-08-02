import os
from os.path import join as jph
import pickle

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits


def delete_from_path(pfi_file_1, pfi_file_2):
    assert os.path.exists(pfi_file_1), pfi_file_1

    cmd = 'rm -r {}'.format(pfi_file_1)
    print_and_run(cmd)

    if os.path.exists(pfi_file_2):
        cmd = 'rm -r {}'.format(pfi_file_2)
        print_and_run(cmd)


def delete_unzipped_raw_data_single_subject(sj):
    print('- Unzip subject {} '.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    # to 00_raw_data_unzipped_TMP
    pfi_raw_unzipped = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj)
    pfi_file_for_MAC = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, '__MACOSX')

    delete_from_path(pfi_raw_unzipped, pfi_file_for_MAC)

    # Check for external files
    # |---> Secondary study to be merged. If any convert it as well (conversion must have happened in module B_).
    sj_exts = sj_parameters['merge_with']
    if sj_exts is not None:
        for sj_ext in sj_exts:
            pfi_raw_unzipped = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj_ext)
            pfi_file_for_MAC = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, '__MACOSX')

            delete_from_path(pfi_raw_unzipped, pfi_file_for_MAC)


def delete_unzipped_raw_data_from_list(subj_list):
    print '\n\n DELETING TMP CONVERTED SUBJECTS {} \n'.format(subj_list)
    for sj in subj_list:
        delete_unzipped_raw_data_single_subject(sj)


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['125930', ]
    lsm.update_ls()

    print lsm.ls

    delete_unzipped_raw_data_from_list(lsm.ls)
