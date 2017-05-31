import os
import numpy as np
from os.path import join as jph

from definitions import root_study_rabbits, pfi_excel_table_ACS, pfi_excel_table_PTB, pfi_excel_table_PTB_templ

from pipeline_project.A0_main.main_controller import subject, RunParameters


def save_data_into_excel_file(sj):




    # grab excel table
    if subject[sj][0][0] == 'ACS':
        pfi_excel_table = pfi_excel_table_ACS
    elif subject[sj][0][0] == 'PTB':
        pfi_excel_table = pfi_excel_table_PTB



    print rp


def save_data_into_excel_file_for_group(pfo_group, bypass_subjects=None):

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


def execute_saver_into_excel_file(rp):

    assert isinstance(rp, RunParameters)
    root_raw_data = jph(root_study_rabbits, '00_raw_data')
    root_destination = jph(root_study_rabbits, 'A_data')

    if rp.execute_PTB_ex_skull:
        study = 'PTB'
        category = 'ex_skull'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        save_data_into_excel_file_for_group(pfo_source,  bypass_subjects=rp.subjects)

    if rp.execute_PTB_ex_vivo:
        study = 'PTB'
        category = 'ex_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        save_data_into_excel_file_for_group(pfo_source, bypass_subjects=rp.subjects)

    if rp.execute_PTB_in_vivo:
        study = 'PTB'
        category = 'in_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        save_data_into_excel_file_for_group(pfo_source, bypass_subjects=rp.subjects)

    if rp.execute_PTB_op_skull:
        study = 'PTB'
        category = 'op_skull'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        save_data_into_excel_file_for_group(pfo_source, bypass_subjects=rp.subjects)

    if rp.execute_ACS_ex_vivo:
        study = 'ACS'
        category = 'ex_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        save_data_into_excel_file_for_group(pfo_source, bypass_subjects=rp.subjects)


if __name__ == '__main__':

    rpa = RunParameters()

    rpa.execute_PTB_ex_skull = True
    rpa.execute_PTB_ex_vivo = True
    rpa.execute_PTB_in_vivo = True
    rpa.execute_PTB_op_skull = True
    rpa.execute_ACS_ex_vivo = True

    rpa.subjects = None
    rpa.update_params()

    execute_saver_into_excel_file(rpa)
