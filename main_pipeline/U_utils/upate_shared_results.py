"""
Update results on the shared Dropbox folder with Hannes
"""

import os
from os.path import join as jph
import pickle

from tools.definitions import root_study_rabbits, root_shared_records, pfi_excel_table_all_data, pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.utils import print_and_run


def send_or_erase(sj, pfo_source, pfo_destination, records_only=False,
                  erase_source=False, erase_destination=False):
    # copy records template if any
    folder_destination_reports = jph(pfo_destination, sj)
    cmd0 = 'mkdir -p {}'.format(folder_destination_reports)
    print_and_run(cmd0)

    if sj is not None:
        if erase_source:
            cmd = 'rm -r {}'.format(jph(pfo_source, sj))
            print_and_run(cmd)
            print(cmd)
        elif erase_destination:
            cmd = 'rm -r {}'.format(jph(pfo_destination, sj))
            print_and_run(cmd)
            print(cmd)
        else:
            # copy records
            folder_source_reports = jph(pfo_source, sj, 'records')
            folder_destination_reports = jph(pfo_destination, sj)
            cmd0 = 'mkdir -p {}'.format(folder_destination_reports)
            print_and_run(cmd0)

            if os.path.exists(folder_source_reports):
                cmd1 = 'cp -r {} {} '.format(folder_source_reports, folder_destination_reports)
                print_and_run(cmd1)
                print(cmd1)
            else:
                print('REPORTS for subject {} not present'.format(sj))
                return

            folder_source_reports = jph(pfo_source, sj, 'records_template')
            if os.path.exists(folder_source_reports):
                cmd1 = 'cp -r {} {} '.format(folder_source_reports, folder_destination_reports)
                print_and_run(cmd1)
                print(cmd1)

            if not records_only:
                # copy mod
                folder_source_mod = jph(pfo_source, sj, 'mod')
                folder_destination_mod = jph(pfo_destination, sj)
                cmd0 = 'mkdir -p {}'.format(folder_destination_mod)
                print_and_run(cmd0)

                if os.path.exists(folder_source_mod):
                    cmd1 = 'cp -r {} {} '.format(folder_source_mod, folder_destination_mod)
                    print_and_run(cmd1)
                    print(cmd1)
                else:
                    print('MOD for subject {} not present'.format(sj))
                # copy segm
                folder_source_segm = jph(pfo_source, sj, 'segm')
                folder_destination_segm = jph(pfo_destination, sj)
                cmd0 = 'mkdir -p {}'.format(folder_destination_segm)
                print_and_run(cmd0)

                if os.path.exists(folder_source_segm):
                    cmd1 = 'cp -r {} {} '.format(folder_source_segm, folder_destination_segm)
                    print_and_run(cmd1)
                    print(cmd1)
                else:
                    print('REPORTS for subject {} not present'.format(sj))


def send_data_to_hannes_from_list(subj_list, records_only=False, erase_source=False, erase_destination=False,
                                  send_excel_table=False):

    root_data    = jph(root_study_rabbits, 'A_data')

    if os.path.exists(root_shared_records):

        # copy excel file
        if send_excel_table:
            if os.path.exists(pfi_excel_table_all_data):
                cmd1 = 'cp {} {} '.format(pfi_excel_table_all_data, jph(root_shared_records, 'REoP_Data.xlsx'))
                print_and_run(cmd1)
                print(cmd1)

        for sj in subj_list:

            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

            study = sj_parameters['study']
            category = sj_parameters['category']
            pfo_source = jph(root_data, study, category)

            assert os.path.exists(pfo_source)
            pfo_destination = jph(root_shared_records, study, category)
            send_or_erase(sj, pfo_source, pfo_destination, records_only=records_only, erase_source=erase_source,
                          erase_destination=erase_destination)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = True
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    # lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    send_data_to_hannes_from_list(lsm.ls, records_only=True, send_excel_table=True)
