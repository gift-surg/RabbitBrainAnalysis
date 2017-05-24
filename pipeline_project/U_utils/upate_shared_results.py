"""
Update results on the shared Dropbox folder with Hannes
"""

import os
from os.path import join as jph

import numpy as np

from definitions import root_pilot_study_dropbox, root_pilot_study_pantopolium
from pipeline_project.A0_main.main_controller import RunParameters


def send_or_erase(rp, pfo_source, pfo_destination, records_only=False, erase=False):

    subj_list = np.sort(list(set(os.listdir(pfo_source)) - {'.DS_Store'}))
    if rp.subjects is not None:
        subj_list = rp.subjects

    for sj in subj_list:

        if erase:
            cmd = 'rm -r {}'.format(jph(pfo_source, sj))
            os.system(cmd)
            print(cmd)
        else:
            # copy records
            folder_source_reports = jph(pfo_source, sj, 'records')
            folder_destination_reports = jph(pfo_destination, sj)
            cmd0 = 'mkdir -p {}'.format(folder_destination_reports)
            os.system(cmd0)

            if os.path.exists(folder_source_reports):
                cmd1 = 'cp -r {} {} '.format(folder_source_reports, folder_destination_reports)
                os.system(cmd1)
                print(cmd1)
            else:
                print('REPORTS for subject {} not present'.format(sj))
                return

            if not records_only:
                # copy mod
                folder_source_mod = jph(pfo_source, sj, 'mod')
                folder_destination_mod = jph(pfo_destination, sj)
                cmd0 = 'mkdir -p {}'.format(folder_destination_mod)
                os.system(cmd0)

                if os.path.exists(folder_source_mod):
                    cmd1 = 'cp -r {} {} '.format(folder_source_mod, folder_destination_mod)
                    os.system(cmd1)
                    print(cmd1)
                else:
                    print('MOD for subject {} not present'.format(sj))
                # copy segm
                folder_source_segm = jph(pfo_source, sj, 'segm')
                folder_destination_segm = jph(pfo_destination, sj)
                cmd0 = 'mkdir -p {}'.format(folder_destination_segm)
                os.system(cmd0)

                if os.path.exists(folder_source_segm):
                    cmd1 = 'cp -r {} {} '.format(folder_source_segm, folder_destination_segm)
                    os.system(cmd1)
                    print(cmd1)
                else:
                    print('REPORTS for subject {} not present'.format(sj))


def send_data_to_hannes(rp, records_only=False, erase=False):

    assert os.path.isdir(root_pilot_study_pantopolium), 'Connect pantopolio!'
    assert isinstance(rp, RunParameters)

    root_data    = jph(root_pilot_study_pantopolium, 'A_data')
    root_dropbox_reports = jph(root_pilot_study_dropbox, 'C_records')

    assert os.path.isdir(root_data)
    assert os.path.isdir(root_dropbox_reports)

    if rp.execute_PTB_ex_skull:
        group = 'PTB'
        category = 'ex_skull'
        pfo_source = jph(root_data, group, category)
        assert os.path.exists(pfo_source)
        pfo_destination = jph(root_dropbox_reports, group, category)
        send_or_erase(rp, pfo_source, pfo_destination, records_only=records_only, erase=erase)

    if rp.execute_PTB_ex_vivo:
        group = 'PTB'
        category = 'ex_vivo'
        pfo_source = jph(root_data, group, category)
        assert os.path.exists(pfo_source)
        pfo_destination = jph(root_dropbox_reports, group, category)
        send_or_erase(rp, pfo_source, pfo_destination, records_only=records_only, erase=erase)

    if rp.execute_PTB_in_vivo:
        group = 'PTB'
        category = 'in_vivo'
        pfo_source = jph(root_data, group, category)
        assert os.path.exists(pfo_source)
        pfo_destination = jph(root_dropbox_reports, group, category)
        send_or_erase(rp, pfo_source, pfo_destination, records_only=records_only, erase=erase)

    if rp.execute_PTB_op_skull:
        group = 'PTB'
        category = 'op_skull'
        pfo_source = jph(root_data, group, category)
        assert os.path.exists(pfo_source)
        pfo_destination = jph(root_dropbox_reports, group, category)
        send_or_erase(rp, pfo_source, pfo_destination, records_only=records_only, erase=erase)

    if rp.execute_ACS_ex_vivo:
        group = 'ACS'
        category = 'ex_vivo'
        pfo_source = jph(root_data, group, category)
        assert os.path.exists(pfo_source)
        pfo_destination = jph(root_dropbox_reports, group, category)
        send_or_erase(rp, pfo_source, pfo_destination, records_only=records_only, erase=erase)


if __name__ == '__main__':

    rpa = RunParameters()

    # rpa.execute_PTB_ex_skull = False
    # rpa.execute_PTB_ex_vivo = True
    # rpa.execute_PTB_in_vivo = True
    # rpa.execute_PTB_op_skull = False
    # rpa.execute_ACS_ex_vivo = False

    # rpa.subjects = None
    # rpa.update_params()
    rpa.subjects = ['2702', ]
    rpa.update_params()

    send_data_to_hannes(rpa)
