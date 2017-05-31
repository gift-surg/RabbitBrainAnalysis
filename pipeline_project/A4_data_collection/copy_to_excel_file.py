import os
import numpy as np
import pandas as pd
import xlwings as xw
from os.path import join as jph

from definitions import root_study_rabbits, pfi_excel_table_ACS, pfi_excel_table_PTB, pfi_excel_table_PTB_templ
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager, templ_subjects


def store_records_in_excel_table(sj, pfi_record, pfi_excel_table):


    target_df = xw.Range('A7').options(pd.DataFrame,
                                       expand='table').value  # only do this if the 'A7' cell (the cell within area of interest) is in active worksheet
    # otherwise do:
    # sht = xw.Book(r'path to your xlxs file\name_of_file.xlsx`).sheets['name of sheet']
    # target_df = sht.Range('A7').options(pd.DataFrame, expand='table').value # you can also change 'A7' to any name that you've given to a cell like 'interest_table`

    # START HERE http://openpyxl.readthedocs.io/en/default/tutorial.html (no pandas!)
    # THEN maybe  HERE: https://stackoverflow.com/questions/20219254/how-to-write-to-an-existing-excel-file-without-overwriting-data-using-pandas
    # https://stackoverflow.com/questions/28142420/can-pandas-read-and-modify-a-single-excel-file-worksheet-tab-without-modifying
    # http://openpyxl.readthedocs.io/en/default/tutorial.html


    assert os.path.exists(pfi_record)
    assert os.path.exists(pfi_excel_table)

    record_dict = np.load(pfi_record)
    record_dict = record_dict.item()

    assert record_dict['Info']['ID Number'] == sj

    print sj
    print record_dict
    print pfi_excel_table

    import pandas as pd

    df = pd.read_excel(pfi_excel_table)  # data frame

    writer = pd.ExcelWriter('/Users/sebastiano/Desktop/zzzz.xlsx')
    df.to_excel(writer, 'Sheet1')
    df.to_excel(writer, 'Sheet2')
    writer.save()

    print df.head()


def save_data_into_excel_file_per_subject(sj):
    group = subject[sj][0][0]
    category = subject[sj][0][1]
    pfo_records = jph(root_study_rabbits, 'A_data', group, category, sj, 'records')
    records_exists = False
    if os.path.exists(pfo_records):
        records_exists = True
    if records_exists:
        # get subject records
        pfi_record = jph(pfo_records, sj + '_record.npy')
        assert os.path.exists(pfi_record)
        # get pfi excel table
        if group == 'ACS':
            pfi_excel_table = pfi_excel_table_ACS
        elif group == 'PTB':
            pfi_excel_table = pfi_excel_table_PTB
        else:
            raise IOError
        # ---------
        store_records_in_excel_table(sj, pfi_record, pfi_excel_table)
        # ---------
    else:
        msg = 'Record folder not present for the subject {} '.format(sj)
        print(msg)

    if sj in templ_subjects:
        pfo_records = jph(root_study_rabbits, 'A_data', group, category, sj, 'records_template')
        records_template_exists = False
        if os.path.exists(pfo_records):
            records_template_exists = True
        if records_template_exists:
            # get subject records
            pfi_record = jph(pfo_records, sj + '_record.npy')
            # get pfi excel table
            pfi_excel_table = pfi_excel_table_PTB_templ
            # -------------
            store_records_in_excel_table(sj, pfi_record, pfi_excel_table)
            # -------------
        else:
            msg = 'Record_template folder not present for the subject {} '.format(sj)
            print(msg)


def save_data_into_excel_file_for_list(subj_list):
    print '\n\n SAVING DATA IN EXCEL FILE in {} \n'.format(subj_list)
    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)
        save_data_into_excel_file_per_subject(sj)


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
