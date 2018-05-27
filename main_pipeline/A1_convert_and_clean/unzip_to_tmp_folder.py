import os
from os.path import join as jph
import pickle

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits
from LABelsToolkit.tools.aux_methods.utils import print_and_run


def unzip_single_sj(sj):

    print('- Unzip subject {} '.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    # from 00_raw_data
    pfi_input_sj_zip = jph(root_study_rabbits, '00_raw_data_zipped', study, category, '{}.zip'.format(sj))
    assert os.path.exists(pfi_input_sj_zip), 'Zipped file {} does not exists'.format(pfi_input_sj_zip)

    # to 00_raw_data_unzipped_TMP
    pfo_output = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category)

    # Unizp:
    cmd = 'tar -xvf {} -C {}'.format(pfi_input_sj_zip, pfo_output)
    print cmd
    print_and_run(cmd)

    # Rename:
    file_found = 0
    for p in os.listdir(pfo_output):

        if '_HVDM_{}_'.format(sj) in p:
            file_found += 1
            pfi_unzipped_old_name = jph(pfo_output, p)
            pfi_unzipped_new_name = jph(pfo_output, sj)
            cmd = 'mv {} {}'.format(pfi_unzipped_old_name, pfi_unzipped_new_name)
            print_and_run(cmd)
            break

    if file_found != 1:
        raise IOError('Unzipped file was saved with a different naming convention. We found {} with string {} in it. '
                      'Manual work required.'.format(file_found, '_HVDM_{}_'.format(sj)))


def unzip_subjects_from_list(subj_list):
    print('\n\n UNZIPPING SUBJECTS {} \n'.format(subj_list))
    for sj in subj_list:
        unzip_single_sj(sj)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['13202', ]
    lsm.update_ls()

    print lsm.ls

    unzip_subjects_from_list(lsm.ls)
