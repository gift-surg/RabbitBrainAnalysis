import os
import numpy as np
from os.path import join as jph

from definitions import root_study_rabbits, pfi_excel_table_ACS, pfi_excel_table_PTB, pfi_excel_table_PTB_templ

from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager


def save_data_into_excel_file(sj):


    visu_pars_dict.item().get('VisuAcqEchoTime')

    # grab excel table
    if subject[sj][0][0] == 'ACS':
        pfi_excel_table = pfi_excel_table_ACS
    elif subject[sj][0][0] == 'PTB':
        pfi_excel_table = pfi_excel_table_PTB



    print rp


def save_data_into_excel_file_for_list(pfo_group, bypass_subjects=None):

    assert os.path.exists(pfo_group)

    subj_list = np.sort(list(set(os.listdir(pfo_group)) - {'.DS_Store'}))

    if bypass_subjects is not None:
        if set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n SAVING DATA IN EXCEL FILE in {}\n {} \n'.format(pfo_group, subj_list)

    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)
        save_data_into_excel_file(sj)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    save_data_into_excel_file_for_list(lsm.ls)
