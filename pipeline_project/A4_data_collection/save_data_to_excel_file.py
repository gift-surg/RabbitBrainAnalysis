import os
from os.path import join as jph
import pickle
from tools.definitions import root_study_rabbits, pfi_excel_table_all_data, pfo_subjects_parameters
from pipeline_project.A0_main.main_controller import ListSubjectsManager
from pipeline_project.A0_main.subject_parameters_manager import get_list_names_subjects_in_template
from tools.auxiliary.parse_excel_tables_and_descriptors import store_a_record_in_excel_table


def save_data_into_excel_file_per_subject(sj):

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    group = sj_parameters['group']
    category = sj_parameters['category']
    pfo_records = jph(root_study_rabbits, 'A_data', group, category, sj, 'records')
    records_exists = False
    if os.path.exists(pfo_records):
        records_exists = True
    if records_exists:
        # get subject records
        pfi_record = jph(pfo_records, sj + '_record.npy')
        assert os.path.exists(pfi_record)
        # ---------
        store_a_record_in_excel_table(pfi_record, pfi_excel_table_all_data, sj, group)
        # ---------
        if sj in get_list_names_subjects_in_template(pfo_subjects_parameters):
            pfi_record_template = jph(root_study_rabbits, 'A_data', group, category, sj, 'records_template',
                                      sj + '_record.npy')
            if os.path.exists(pfi_record_template):
                store_a_record_in_excel_table(pfi_record_template, pfi_excel_table_all_data, sj, 'Template')
            else:
                msg = 'Record_template folder not present for the subject {} '.format(sj)
                print(msg)

    else:
        msg = 'Record folder not present for the subject {} '.format(sj)
        print(msg)


def save_data_into_excel_file_for_list(subj_list):
    print '\n\n SAVING DATA IN EXCEL FILE in {} \n'.format(subj_list)
    for sj in subj_list:
        print 'Subj {} saving in the excel table...\n'.format(sj)
        save_data_into_excel_file_per_subject(sj)
        print('Saved.\n')


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = True

    lsm.input_subjects = ['1201', ]  # '2502' [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    save_data_into_excel_file_for_list(lsm.ls)
